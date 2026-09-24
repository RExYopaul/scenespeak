"""Database helpers and SQLite persistence for SceneSpeak.

Implements the data schema specified in Section 13 of the SceneSpeak PDR:
- Table `scenes`: stores request trace metadata, cleaned response, flags, and latency.
- Table `feedback`: stores 1-5 star ratings and user feedback notes.

PRIVACY GUARANTEE:
Per Section 5 & 13.3 of the PDR: No images, personal identifiers, or raw GPS
coordinates are EVER stored in the database or written to disk.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.config import settings

# Parse the database file path from SQLite URL
DB_PATH = Path(settings.database_url.replace("sqlite:///", ""))


def get_connection() -> sqlite3.Connection:
    """Creates a connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes the SQLite database tables if they do not already exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()
        # scenes table (PDR Section 13.2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenes (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                mode TEXT NOT NULL,
                response_text TEXT NOT NULL,
                hazard INTEGER NOT NULL,
                retake INTEGER NOT NULL,
                latency_ms INTEGER NOT NULL,
                model TEXT NOT NULL
            )
        """)

        # feedback table (PDR Section 13.2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (scene_id) REFERENCES scenes (id)
            )
        """)
        conn.commit()


# Automatically initialize the database tables on import
init_db()


def log_scene(
    request_id: str,
    mode: str,
    response_text: str,
    hazard: bool,
    retake: bool,
    latency_ms: int,
    model: str,
) -> None:
    """Logs scene description metadata. Note: NO image data is saved."""
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO scenes (id, created_at, mode, response_text, hazard, retake, latency_ms, model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                created_at,
                mode,
                response_text,
                1 if hazard else 0,
                1 if retake else 0,
                latency_ms,
                model,
            ),
        )
        conn.commit()


def log_feedback(
    scene_id: str,
    rating: int,
    note: Optional[str] = None,
) -> None:
    """Logs user feedback (1 to 5 stars)."""
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO feedback (scene_id, rating, note, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (scene_id, rating, note, created_at),
        )
        conn.commit()


def get_stats() -> Dict[str, Any]:
    """Computes aggregate metrics for the demo evaluation slide (Section 14.1)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                COALESCE(AVG(latency_ms), 0.0) as avg_latency_ms,
                COALESCE(AVG(retake), 0.0) as retake_rate,
                COALESCE(AVG(hazard), 0.0) as hazard_rate
            FROM scenes
        """)
        row = cursor.fetchone()
        return {
            "total_requests": row["total_requests"],
            "avg_latency_ms": round(float(row["avg_latency_ms"]), 1),
            "retake_rate": round(float(row["retake_rate"]), 3),
            "hazard_rate": round(float(row["hazard_rate"]), 3),
        }
