import aiosqlite
from datetime import datetime
from typing import Optional
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "chat.db")

db: Optional[aiosqlite.Connection] = None


async def connect_to_db():
    global db
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row

    # Create tables
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            _id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            _id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            is_ai INTEGER DEFAULT 0
        )
    """)

    await db.commit()
    print(f"Connected to SQLite database: {DATABASE_PATH}")


async def close_db_connection():
    global db
    if db:
        await db.close()
        print("Closed SQLite connection")


def get_database():
    """Returns a database wrapper with collection-like interface"""
    from sqlite_db import SQLiteDatabase
    return SQLiteDatabase()


# Aliases for compatibility
connect_to_mongo = connect_to_db
close_mongo_connection = close_db_connection
