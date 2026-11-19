"""
AgroSense AI - Database Management Layer
Handles SQLite persistence for chat sessions, source citations, soil evaluations, and query analytics.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables if they do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Chat history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources_json TEXT DEFAULT '[]',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                feedback INTEGER DEFAULT 0
            )
            """
        )

        # Soil evaluations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS soil_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                farmer_name TEXT,
                field_location TEXT,
                target_crop TEXT,
                ph REAL,
                ec REAL,
                oc REAL,
                n REAL,
                p REAL,
                k REAL,
                status_summary TEXT,
                recommendations_json TEXT
            )
            """
        )

        # Telemetry / Query Analytics
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query_text TEXT,
                provider TEXT,
                latency_ms REAL,
                sources_count INTEGER
            )
            """
        )

        conn.commit()


# Chat History Operations
def save_chat_message(session_id: str, role: str, content: str, sources: Optional[List[Dict[str, Any]]] = None) -> int:
    """Persists a chat message to SQLite."""
    sources_json = json.dumps(sources or [])
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history (session_id, role, content, sources_json)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, sources_json),
        )
        conn.commit()
        return cursor.lastrowid


def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Fetches chat transcript for a given session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, session_id, role, content, sources_json, timestamp, feedback
            FROM chat_history
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,),
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "session_id": r["session_id"],
                "role": r["role"],
                "content": r["content"],
                "sources": json.loads(r["sources_json"] or "[]"),
                "timestamp": r["timestamp"],
                "feedback": r["feedback"]
            })
        return result


def clear_chat_history(session_id: Optional[str] = None):
    """Clears history for a session or entirely."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if session_id:
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        else:
            cursor.execute("DELETE FROM chat_history")
        conn.commit()


# Soil Records Operations
def save_soil_record(
    farmer_name: str,
    field_location: str,
    target_crop: str,
    ph: float,
    ec: float,
    oc: float,
    n: float,
    p: float,
    k: float,
    status_summary: str,
    recommendations: Dict[str, Any]
) -> int:
    """Saves a soil test evaluation record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO soil_records (
                farmer_name, field_location, target_crop, ph, ec, oc, n, p, k,
                status_summary, recommendations_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer_name,
                field_location,
                target_crop,
                ph,
                ec,
                oc,
                n,
                p,
                k,
                status_summary,
                json.dumps(recommendations)
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_recent_soil_records(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns recent soil test evaluations."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM soil_records ORDER BY id DESC LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "farmer_name": r["farmer_name"],
                "field_location": r["field_location"],
                "target_crop": r["target_crop"],
                "ph": r["ph"],
                "ec": r["ec"],
                "oc": r["oc"],
                "n": r["n"],
                "p": r["p"],
                "k": r["k"],
                "status_summary": r["status_summary"],
                "recommendations": json.loads(r["recommendations_json"] or "{}")
            })
        return results


# Analytics Operations
def log_analytics(query_text: str, provider: str, latency_ms: float, sources_count: int):
    """Logs query telemetry."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analytics_events (query_text, provider, latency_ms, sources_count)
            VALUES (?, ?, ?, ?)
            """,
            (query_text, provider, latency_ms, sources_count)
        )
        conn.commit()


def get_analytics_summary() -> Dict[str, Any]:
    """Retrieves operational telemetry for dashboard."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_queries FROM analytics_events")
        total_queries = cursor.fetchone()["total_queries"]

        cursor.execute("SELECT AVG(latency_ms) as avg_latency FROM analytics_events")
        avg_lat = cursor.fetchone()["avg_latency"] or 0.0

        cursor.execute("SELECT COUNT(*) as total_soil_tests FROM soil_records")
        total_soil = cursor.fetchone()["total_soil_tests"]

        cursor.execute("SELECT COUNT(*) as total_messages FROM chat_history")
        total_msgs = cursor.fetchone()["total_messages"]

        return {
            "total_queries": total_queries,
            "avg_latency_ms": round(avg_lat, 2),
            "total_soil_tests": total_soil,
            "total_messages": total_msgs
        }


# Auto-init on import
init_db()
