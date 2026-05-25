"""
CPIRS - Document Collection
============================
In-memory document store managed by a container.
"""

from __future__ import annotations
from typing import List, Optional
from .models import Document


class DocumentCollection:
    """Manages an ordered set of Documents for one container."""

    def __init__(self, name: str = "default"):
        self.name = name
        self._store: dict[str, Document] = {}

    def add(self, doc: Document) -> None:
        self._store[doc.doc_id] = doc

    def remove(self, doc_id: str) -> bool:
        return self._store.pop(doc_id, None) is not None

    def get(self, doc_id: str) -> Optional[Document]:
        return self._store.get(doc_id)

    def all(self) -> List[Document]:
        return list(self._store.values())

    def size(self) -> int:
        return len(self._store)

    def __repr__(self):
        return f"DocumentCollection(name={self.name!r}, docs={self.size()})"