"""
CPIRS - Platform
================
A Platform owns a group of Containers.
Inter-platform migration crosses Platform boundaries.
"""

from __future__ import annotations
import logging
from typing import List, Optional

from ..containers.container import Container

logger = logging.getLogger("cpirs.platform")


class Platform:
    """
    A logical execution environment that hosts one or more Containers.

    In a real JADE/JADE-like deployment each Platform would run on a
    different host (AMS + DF agents).  Here we simulate it in-process.
    """

    def __init__(self, platform_id: str):
        self.platform_id  = platform_id
        self._containers  : dict[str, Container] = {}

    # ── Container registry ─────────────────────────────────────────────────
    def register_container(self, container: Container) -> None:
        container.platform_id = self.platform_id
        self._containers[container.name] = container
        logger.info(f"[Platform {self.platform_id}] Registered container '{container.name}'")

    def get_container(self, name: str) -> Optional[Container]:
        return self._containers.get(name)

    def all_containers(self) -> List[Container]:
        return list(self._containers.values())

    def container_count(self) -> int:
        return len(self._containers)

    def __repr__(self):
        return (f"Platform(id={self.platform_id!r}, "
                f"containers={list(self._containers.keys())})")
