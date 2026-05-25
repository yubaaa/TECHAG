"""
CPIRS - Container
=================
A Container manages a DocumentCollection and answers SearchRequests.
It is the destination the mobile BuyerAgent visits.
"""

from __future__ import annotations
import logging
from typing import Optional

from ..core.models import SearchRequest, SearchResponse
from ..core.collection import DocumentCollection
from ..core.relevance import RelevanceEngine

logger = logging.getLogger("cpirs.container")


class Container:
    """
    Represents one node in the CPIRS network.

    Attributes
    ----------
    name        : human-readable identifier
    platform_id : which platform this container belongs to
    collection  : the set of documents managed here
    """

    def __init__(self, name: str, platform_id: str = "default_platform"):
        self.name        = name
        self.platform_id = platform_id
        self.collection  = DocumentCollection(name=name)
        self._engine     = RelevanceEngine()

    # ── Document management ────────────────────────────────────────────────
    def add_document(self, doc) -> None:
        self.collection.add(doc)
        logger.debug(f"[Container {self.name}] Added doc '{doc.title}'")

    # ── Request handling  (called by the mobile agent) ─────────────────────
    def handle_request(self, request: SearchRequest) -> SearchResponse:
        logger.debug(f"[Container {self.name}] Handling request '{request.query}'")
        docs = self.collection.all()
        ranked = self._engine.rank(docs, request)[: request.max_results]
        return SearchResponse(
            request_id       = request.request_id,
            documents        = ranked,
            source_container = self.name,
            source_platform  = self.platform_id,
        )

    def __str__(self):
        return f"{self.platform_id}/{self.name}"

    def __repr__(self):
        return (f"Container(name={self.name!r}, platform={self.platform_id!r}, "
                f"docs={self.collection.size()})")
