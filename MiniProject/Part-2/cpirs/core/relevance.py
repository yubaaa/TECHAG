"""
CPIRS - Relevance Engine
========================
Computes personalised relevance score for (document, request) pairs.
"""

from __future__ import annotations
from typing import List
from .models import Document, SearchRequest


class RelevanceEngine:
    """
    Scores documents against a query + user profile.
    Score = keyword_overlap  +  category_boost  +  profile_boost
    All normalised to [0, 1].
    """

    def score(self, doc: Document, request: SearchRequest) -> float:
        query_tokens = set(request.query.lower().split())
        doc_tokens   = set(" ".join([doc.title, doc.content, *doc.keywords]).lower().split())

        # 1. Keyword overlap  (0..1)
        overlap = len(query_tokens & doc_tokens) / max(len(query_tokens), 1)

        # 2. Profile boost  (0..0.4)
        profile_boost = 0.0
        if request.user_profile:
            profile_tokens = set(
                " ".join(request.user_profile.keywords_of_interest).lower().split()
            )
            profile_boost = 0.4 * len(profile_tokens & doc_tokens) / max(len(profile_tokens), 1)

        # 3. Category match  (0 or 0.2)
        category_boost = 0.0
        if request.user_profile and doc.category in request.user_profile.preferred_categories:
            category_boost = 0.2

        return min(overlap + profile_boost + category_boost, 1.0)

    def rank(self, docs: List[Document], request: SearchRequest) -> List[Document]:
        for doc in docs:
            doc.relevance_score = self.score(doc, request)
        return sorted(docs, key=lambda d: d.relevance_score, reverse=True)
