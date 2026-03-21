"""
SQLite Database Wrapper for the chat application.
Provides a MongoDB-like interface for users and messages collections.
"""
import aiosqlite
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
from database import db


class SQLiteCollection:
    def __init__(self, table_name: str):
        self.table_name = table_name

    async def insert_one(self, document: dict) -> Any:
        doc_id = document.get('_id') or str(uuid.uuid4())
        document['_id'] = doc_id

        # Convert datetime to ISO format string
        if 'created_at' in document and isinstance(document['created_at'], datetime):
            document['created_at'] = document['created_at'].isoformat()
        if 'timestamp' in document and isinstance(document['timestamp'], datetime):
            document['timestamp'] = document['timestamp'].isoformat()
        if 'is_ai' in document:
            document['is_ai'] = 1 if document['is_ai'] else 0

        columns = ', '.join(document.keys())
        placeholders = ', '.join(['?' for _ in document])
        values = list(document.values())

        async with db.execute(f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})", values):
            await db.commit()

        return type('InsertResult', (), {'inserted_id': doc_id})()

    async def find_one(self, query: dict) -> Optional[dict]:
        where_clause, values = self._build_where(query)
        async with db.execute(f"SELECT * FROM {self.table_name} {where_clause}", values) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_dict(row)
        return None

    def find(self, query: dict = None):
        query = query or {}
        return SQLiteCursor(self.table_name, query)

    def _build_where(self, query: dict) -> tuple:
        conditions = []
        values = []

        for key, value in query.items():
            if key == '$or':
                or_conditions = []
                for q in value:
                    sub_where, sub_values = self._build_where(q)
                    or_conditions.append(sub_where)
                    values.extend(sub_values)
                conditions.append(f"({' OR '.join(or_conditions)})")
            elif key == '$ne':
                pass  # Handle $ne in the calling code
            elif isinstance(value, dict):
                for op, op_value in value.items():
                    if op == '$eq':
                        conditions.append(f"{key} = ?")
                        values.append(op_value)
                    elif op == '$in':
                        placeholders = ', '.join(['?' for _ in op_value])
                        conditions.append(f"{key} IN ({placeholders})")
                        values.extend(op_value)
                    elif op == '$ne':
                        conditions.append(f"{key} != ?")
                        values.append(op_value)
            else:
                conditions.append(f"{key} = ?")
                values.append(value)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, values

    def _row_to_dict(self, row: aiosqlite.Row) -> dict:
        d = dict(row)
        # Convert is_ai back to boolean
        if 'is_ai' in d:
            d['is_ai'] = bool(d['is_ai'])
        return d


class SQLiteCursor:
    def __init__(self, table_name: str, query: dict):
        self.table_name = table_name
        self.query = query
        self._sort_key = None
        self._sort_dir = 1
        self._limit_count = None

    def sort(self, key: str, direction: int = -1):
        self._sort_key = key
        self._sort_dir = direction
        return self

    def limit(self, count: int):
        self._limit_count = count
        return self

    async def to_list(self, count: int = None):
        limit = count or self._limit_count

        where_clause, values = self._build_where(self.query)
        query = f"SELECT * FROM {self.table_name} {where_clause}"

        if self._sort_key:
            direction = "DESC" if self._sort_dir == -1 else "ASC"
            query += f" ORDER BY {self._sort_key} {direction}"

        if limit:
            query += f" LIMIT {limit}"

        results = []
        async with db.execute(query, values) as cursor:
            async for row in cursor:
                d = dict(row)
                if 'is_ai' in d:
                    d['is_ai'] = bool(d['is_ai'])
                results.append(d)

        return results

    def _build_where(self, query: dict) -> tuple:
        conditions = []
        values = []

        for key, value in query.items():
            if key == '$or':
                or_conditions = []
                for q in value:
                    sub_where, sub_values = self._build_where(q)
                    if sub_where:
                        or_conditions.append(sub_where.replace("WHERE ", ""))
                    values.extend(sub_values)
                if or_conditions:
                    conditions.append(f"({' OR '.join(or_conditions)})")
            elif isinstance(value, dict):
                for op, op_value in value.items():
                    if op == '$eq':
                        conditions.append(f"{key} = ?")
                        values.append(op_value)
                    elif op == '$in':
                        placeholders = ', '.join(['?' for _ in op_value])
                        conditions.append(f"{key} IN ({placeholders})")
                        values.extend(op_value)
                    elif op == '$ne':
                        conditions.append(f"{key} != ?")
                        values.append(op_value)
            else:
                conditions.append(f"{key} = ?")
                values.append(value)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, values


class SQLiteDatabase:
    def __getattr__(self, name: str) -> SQLiteCollection:
        return SQLiteCollection(name)

    def __getitem__(self, name: str) -> SQLiteCollection:
        return SQLiteCollection(name)
