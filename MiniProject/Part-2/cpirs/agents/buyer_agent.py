"""
CPIRS - Buyer Agent
====================
Specialised mobile agent that:
  1. Receives a SearchRequest from a user.
  2. Migrates across containers/platforms to collect personalised documents.
  3. Merges and re-ranks results before returning to the user.
"""

from __future__ import annotations
import logging
from typing import List, Optional

from .mobile_agent import MobileAgent, MigrationMode
from ..core.models import SearchRequest, SearchResponse, Document
from ..core.relevance import RelevanceEngine

logger = logging.getLogger("cpirs.buyer_agent")


class BuyerAgent(MobileAgent):
    """
    Mobile Buyer Agent for CPIRS.

    Workflow
    --------
    1. User submits a SearchRequest.
    2. BuyerAgent migrates to each registered container.
    3. At each container it executes a personalised search.
    4. After visiting all containers it merges results globally.
    5. Returns a single ranked list to the user.
    """

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id=agent_id)
        self._engine = RelevanceEngine()

    # ── Main entry point ───────────────────────────────────────────────────
    def search(self,
               request: SearchRequest,
               containers: list,
               migration_mode: MigrationMode = MigrationMode.INTER_CONTAINER,
               ) -> List[Document]:
        """
        High-level API called by the CPIRS system.
        Returns the merged, personalised, ranked list of documents.
        """
        logger.info(
            f"[BuyerAgent {self.agent_id}] New search request '{request.query}' "
            f"for user '{request.user_profile.name if request.user_profile else '?'}' "
            f"| migration_mode={migration_mode.value}"
        )

        # Visit every container (mobile migration happens inside run())
        responses: List[SearchResponse] = self.run(request, containers, migration_mode)

        # Merge all documents from every container
        all_docs: List[Document] = []
        seen_ids = set()
        for resp in responses:
            for doc in resp.documents:
                if doc.doc_id not in seen_ids:
                    seen_ids.add(doc.doc_id)
                    all_docs.append(doc)

        # Global re-rank with the user profile
        ranked = self._engine.rank(all_docs, request)
        top_n  = ranked[: request.max_results]

        logger.info(
            f"[BuyerAgent {self.agent_id}] Returning {len(top_n)} doc(s) "
            f"(merged from {len(all_docs)} total across {len(responses)} container(s))"
        )
        return top_n

    def __repr__(self):
        return (f"BuyerAgent(id={self.agent_id}, state={self.state.name}, "
                f"loc={self.current_location})")
