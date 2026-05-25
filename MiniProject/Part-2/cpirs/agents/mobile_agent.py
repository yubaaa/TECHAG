"""
CPIRS - Mobile Agent
====================
Base class for a mobile agent that can migrate between containers
(inter-container) or between platforms (inter-platform).

State machine:
  IDLE ──► RUNNING ──► MIGRATING ──► RUNNING  (loop)
                   └──► COMPLETED
"""

from __future__ import annotations
import time
import uuid
import copy
import logging
from enum import Enum, auto
from typing import Optional, List

from ..core.models import SearchRequest, SearchResponse

logger = logging.getLogger("cpirs.agent")


class AgentState(Enum):
    IDLE      = auto()
    RUNNING   = auto()
    MIGRATING = auto()
    COMPLETED = auto()
    ERROR     = auto()


class MigrationMode(Enum):
    INTER_CONTAINER = "inter_container"   # same platform, different container
    INTER_PLATFORM  = "inter_platform"    # different platform entirely


class AgentCapsula:
    """
    Serialisable snapshot of an agent's execution state.
    This is what travels over the wire during migration.
    """
    def __init__(self, agent_id: str, request: SearchRequest,
                 pending_containers: list, results: list,
                 migration_mode: MigrationMode, origin: str):
        self.agent_id          = agent_id
        self.request           = request
        self.pending_containers = pending_containers
        self.results           = results
        self.migration_mode    = migration_mode
        self.origin            = origin
        self.timestamp         = time.time()

    def __repr__(self):
        return (f"AgentCapsula(id={self.agent_id}, mode={self.migration_mode.value}, "
                f"pending={len(self.pending_containers)})")


class MobileAgent:
    """
    Abstract mobile buyer agent.

    Subclass and implement `_search_on_container` to connect to a real
    container.  The agent migrates itself by calling
    `migrate(target_container_or_platform, mode)`.
    """

    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id   : str             = agent_id or str(uuid.uuid4())[:8]
        self.state      : AgentState      = AgentState.IDLE
        self.current_location: str        = "unassigned"
        self.results    : List[SearchResponse] = []
        self._request   : Optional[SearchRequest] = None
        self._migration_log: list         = []

    # ── Public API ─────────────────────────────────────────────────────────
    def run(self, request: SearchRequest,
            containers: list,
            migration_mode: MigrationMode) -> List[SearchResponse]:
        """
        Entry-point.  The agent visits each container in *containers*,
        migrating between them according to *migration_mode*.
        """
        self._request = request
        self.state    = AgentState.RUNNING
        pending       = list(containers)          # copy so we can pop

        logger.info(f"[Agent {self.agent_id}] Starting  | mode={migration_mode.value} "
                    f"| containers={[str(c) for c in containers]}")

        while pending:
            target = pending.pop(0)
            self._visit(target)

            if pending:                           # more to visit → migrate
                next_target = pending[0]
                self._migrate(
                    current=target,
                    next_target=next_target,
                    mode=migration_mode,
                    remaining=pending,
                )

        self.state = AgentState.COMPLETED
        logger.info(f"[Agent {self.agent_id}] Completed | collected {len(self.results)} response(s)")
        return self.results

    # ── Internal helpers ────────────────────────────────────────────────────
    def _visit(self, container) -> None:
        """Execute search on `container` and collect result."""
        logger.info(f"[Agent {self.agent_id}] Visiting  container '{container.name}' "
                    f"on platform '{container.platform_id}'")
        self.current_location = f"{container.platform_id}/{container.name}"
        t0 = time.perf_counter()
        response = container.handle_request(self._request)
        response.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.results.append(response)
        logger.info(f"[Agent {self.agent_id}] Got {len(response.documents)} doc(s) "
                    f"from '{container.name}' in {response.elapsed_ms:.1f} ms")

    def _migrate(self, current, next_target, mode: MigrationMode, remaining: list) -> None:
        """
        Simulate agent migration.
        Inter-container : same platform, low overhead.
        Inter-platform  : crosses platform boundary, higher overhead.
        """
        self.state = AgentState.MIGRATING
        capsula = self._pack(next_target, mode, remaining)

        if mode == MigrationMode.INTER_CONTAINER:
            self._inter_container_migrate(current, next_target, capsula)
        else:
            self._inter_platform_migrate(current, next_target, capsula)

        self._unpack(capsula)
        self.state = AgentState.RUNNING

    def _inter_container_migrate(self, src, dst, capsula: AgentCapsula) -> None:
        overhead_ms = 5   # low overhead within same platform
        log_entry = {
            "type"       : MigrationMode.INTER_CONTAINER.value,
            "from"       : f"{src.platform_id}/{src.name}",
            "to"         : f"{dst.platform_id}/{dst.name}",
            "overhead_ms": overhead_ms,
            "timestamp"  : time.time(),
        }
        self._migration_log.append(log_entry)
        time.sleep(overhead_ms / 1000)
        logger.info(f"[Agent {self.agent_id}] ↔  Inter-container migration: "
                    f"'{src.name}' → '{dst.name}'  ({overhead_ms} ms overhead)")

    def _inter_platform_migrate(self, src, dst, capsula: AgentCapsula) -> None:
        overhead_ms = 20  # higher overhead: serialise + network hop
        log_entry = {
            "type"       : MigrationMode.INTER_PLATFORM.value,
            "from"       : f"{src.platform_id}/{src.name}",
            "to"         : f"{dst.platform_id}/{dst.name}",
            "overhead_ms": overhead_ms,
            "timestamp"  : time.time(),
        }
        self._migration_log.append(log_entry)
        time.sleep(overhead_ms / 1000)
        logger.info(f"[Agent {self.agent_id}] ↕  Inter-platform migration: "
                    f"platform '{src.platform_id}' → platform '{dst.platform_id}'  "
                    f"({overhead_ms} ms overhead)")

    def _pack(self, next_target, mode: MigrationMode, remaining: list) -> AgentCapsula:
        """Serialise agent state into a capsula for transport."""
        return AgentCapsula(
            agent_id           = self.agent_id,
            request            = copy.deepcopy(self._request),
            pending_containers = list(remaining),
            results            = list(self.results),
            migration_mode     = mode,
            origin             = self.current_location,
        )

    def _unpack(self, capsula: AgentCapsula) -> None:
        """Restore agent state from capsula after migration."""
        self.agent_id  = capsula.agent_id
        self._request  = capsula.request
        self.results   = capsula.results

    # ── Reporting ──────────────────────────────────────────────────────────
    def migration_summary(self) -> dict:
        return {
            "agent_id"      : self.agent_id,
            "state"         : self.state.name,
            "migrations"    : self._migration_log,
            "total_results" : len(self.results),
        }

    def __repr__(self):
        return f"MobileAgent(id={self.agent_id}, state={self.state.name}, loc={self.current_location})"
