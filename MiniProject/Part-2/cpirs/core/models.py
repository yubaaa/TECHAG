"""
CPIRS - Core Data Models
========================
Document, UserProfile, Query and relevance scoring.
"""

from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ─────────────────────────────────────────────
#  Document
# ─────────────────────────────────────────────
@dataclass
class Document:
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    keywords: List[str] = field(default_factory=list)
    category: str = "general"
    relevance_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content[:80] + "..." if len(self.content) > 80 else self.content,
            "keywords": self.keywords,
            "category": self.category,
            "relevance_score": round(self.relevance_score, 4),
        }

    def __repr__(self):
        return f"Document(id={self.doc_id}, title='{self.title}', category='{self.category}')"


# ─────────────────────────────────────────────
#  User Profile  (personalisation)
# ─────────────────────────────────────────────
@dataclass
class UserProfile:
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:6])
    name: str = "Anonymous"
    preferred_categories: List[str] = field(default_factory=list)
    keywords_of_interest: List[str] = field(default_factory=list)
    language: str = "en"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "preferred_categories": self.preferred_categories,
            "keywords_of_interest": self.keywords_of_interest,
            "language": self.language,
        }


# ─────────────────────────────────────────────
#  Search Request / Response
# ─────────────────────────────────────────────
@dataclass
class SearchRequest:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    query: str = ""
    user_profile: Optional[UserProfile] = None
    max_results: int = 5
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "query": self.query,
            "user": self.user_profile.name if self.user_profile else "?",
            "max_results": self.max_results,
        }


@dataclass
class SearchResponse:
    request_id: str = ""
    documents: List[Document] = field(default_factory=list)
    source_container: str = ""
    source_platform: str = ""
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "results": len(self.documents),
            "source_container": self.source_container,
            "source_platform": self.source_platform,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "documents": [d.to_dict() for d in self.documents],
        }
