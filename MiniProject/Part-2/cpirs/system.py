"""
CPIRS - Main System
===================
Top-level orchestrator that wires Platforms, Containers, and the BuyerAgent.
"""

from __future__ import annotations
import logging
from typing import List, Optional

from .platforms.platform import Platform
from .containers.container import Container
from .agents.buyer_agent import BuyerAgent
from .agents.mobile_agent import MigrationMode
from .core.models import SearchRequest, UserProfile, Document

logger = logging.getLogger("cpirs.system")


class CPIRS:
    """
    Centralised and Personalised Information Retrieval System.

    Usage
    -----
    system = CPIRS()
    system.add_platform(platform)
    results = system.search(query, user_profile, migration_mode=MigrationMode.INTER_CONTAINER)
    """

    def __init__(self, name: str = "CPIRS-1"):
        self.name      = name
        self._platforms: dict[str, Platform] = {}
        logger.info(f"[CPIRS] System '{name}' initialised")

    # ── Platform / Container management ───────────────────────────────────
    def add_platform(self, platform: Platform) -> None:
        self._platforms[platform.platform_id] = platform
        logger.info(f"[CPIRS] Platform '{platform.platform_id}' registered")

    def all_containers(self) -> List[Container]:
        """Flat list of every container across all platforms."""
        containers = []
        for p in self._platforms.values():
            containers.extend(p.all_containers())
        return containers

    # ── Search API ─────────────────────────────────────────────────────────
    def search(self,
               query: str,
               user_profile: Optional[UserProfile] = None,
               max_results: int = 5,
               migration_mode: MigrationMode = MigrationMode.INTER_CONTAINER,
               ) -> List[Document]:
        """
        Main entry point for a user search.

        Parameters
        ----------
        query          : free-text query
        user_profile   : personalisation profile (optional)
        max_results    : maximum documents to return
        migration_mode : INTER_CONTAINER or INTER_PLATFORM
        """
        request = SearchRequest(
            query        = query,
            user_profile = user_profile,
            max_results  = max_results,
        )
        containers = self.all_containers()
        if not containers:
            logger.warning("[CPIRS] No containers registered — returning empty list")
            return []

        agent = BuyerAgent()
        logger.info(
            f"[CPIRS] Dispatching BuyerAgent '{agent.agent_id}' | "
            f"query='{query}' | mode={migration_mode.value} | "
            f"containers={len(containers)}"
        )
        results = agent.search(request, containers, migration_mode)
        self._last_agent = agent   # keep ref for inspection
        return results

    # ── Info ───────────────────────────────────────────────────────────────
    def status(self) -> dict:
        return {
            "system": self.name,
            "platforms": {
                pid: {
                    "containers": [c.name for c in p.all_containers()],
                    "total_docs": sum(c.collection.size() for c in p.all_containers()),
                }
                for pid, p in self._platforms.items()
            },
        }

    def __repr__(self):
        return f"CPIRS(name={self.name!r}, platforms={list(self._platforms.keys())})"
