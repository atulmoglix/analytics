"""
MySQL connection pool for the Semantic MCP server.
Reads credentials from environment variables (loaded via config/.env).
"""

import os
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

_pool: MySQLConnectionPool | None = None


def _get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(
            pool_name="semantic_mcp",
            pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
            host=os.environ["DB_HOST"],
            port=int(os.environ.get("DB_PORT", "3306")),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ.get("DB_META_SCHEMA", "semantic_meta"),
            charset="utf8mb4",
            use_pure=True,
        )
    return _pool


def get_connection():
    """Return a pooled connection. Caller is responsible for closing it."""
    return _get_pool().get_connection()


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT and return rows as list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def query_one(sql: str, params: tuple = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None
