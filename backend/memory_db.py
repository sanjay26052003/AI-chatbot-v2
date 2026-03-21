"""
In-memory database fallback for testing when MongoDB is not available.
This allows testing the authentication and chat functionality without MongoDB.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

class InMemoryInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class InMemoryCollection:
    def __init__(self):
        self.documents: Dict[str, dict] = {}

    async def insert_one(self, document: dict) -> InMemoryInsertResult:
        doc_id = document.get('_id') or str(uuid.uuid4())
        document['_id'] = doc_id
        self.documents[doc_id] = document
        return InMemoryInsertResult(doc_id)

    async def find_one(self, query: dict) -> Optional[dict]:
        for doc in self.documents.values():
            if self._matches(doc, query):
                return doc.copy()
        return None

    def find(self, query: dict = None):
        query = query or {}
        results = [doc.copy() for doc in self.documents.values() if self._matches(doc, query)]
        return InMemoryCursor(results)

    def _matches(self, doc: dict, query: dict) -> bool:
        for key, value in query.items():
            if key.startswith('$'):
                continue  # Skip operators at top level
            if key == '$or':
                if not any(self._matches(doc, q) for q in value):
                    return False
            elif isinstance(value, dict):
                doc_value = doc.get(key)
                for op, op_value in value.items():
                    if op == '$eq' and doc_value != op_value:
                        return False
                    elif op == '$ne' and doc_value == op_value:
                        return False
                    elif op == '$in' and doc_value not in op_value:
                        return False
            else:
                if doc.get(key) != value:
                    return False
        return True


class InMemoryCursor:
    def __init__(self, documents: List[dict]):
        self._documents = documents
        self._limit = None

    def sort(self, key: str, direction: int = -1):
        reverse = direction == -1
        self._documents.sort(key=lambda x: x.get(key) or datetime.min, reverse=reverse)
        return self

    def limit(self, count: int):
        self._limit = count
        self._documents = self._documents[:count]
        return self

    async def to_list(self, count: int = None):
        if count:
            return self._documents[:count]
        return self._documents

    def __iter__(self):
        return iter(self._documents)

    def __aiter__(self):
        self._async_iter = iter(self._documents)
        return self

    def __anext__(self):
        try:
            return next(self._async_iter)
        except StopIteration:
            raise StopAsyncIteration


class InMemoryDatabase:
    def __init__(self):
        self._collections: Dict[str, InMemoryCollection] = {}

    def __getattr__(self, name: str) -> InMemoryCollection:
        if name.startswith('_'):
            raise AttributeError(name)
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]

    def __getitem__(self, name: str) -> InMemoryCollection:
        return getattr(self, name)

    async def create_index(self, *args, **kwargs):
        pass  # No-op for in-memory DB


# Global in-memory database instance
_memory_db: Optional[InMemoryDatabase] = None


def get_memory_database() -> InMemoryDatabase:
    global _memory_db
    if _memory_db is None:
        _memory_db = InMemoryDatabase()
    return _memory_db


def reset_memory_database():
    """Reset the in-memory database - useful for testing"""
    global _memory_db
    _memory_db = InMemoryDatabase()
