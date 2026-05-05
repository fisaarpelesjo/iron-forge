"""SQLite operations for IronForge data."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "ironforge.db"

DEFAULT_EXERCISES = [
    {"name": "Agachamento (barra)", "sets": 3, "reps": 5},
    {"name": "Supino reto (barra)", "sets": 3, "reps": 5},
    {"name": "Remada curvada (barra)", "sets": 3, "reps": 8},
    {"name": "Desenvolvimento (barra em pé)", "sets": 3, "reps": 5},
    {"name": "Stiff com barra", "sets": 3, "reps": 8},
    {"name": "Pullover (barra)", "sets": 3, "reps": 10},
    {"name": "Elevação lateral", "sets": 3, "reps": 10},
    {"name": "Crucifixo invertido", "sets": 3, "reps": 10},
    {"name": "Encolhimento com barra", "sets": 2, "reps": 10},
    {"name": "Rosca direta", "sets": 3, "reps": 8},
    {"name": "Tríceps testa", "sets": 3, "reps": 8},
    {"name": "Wrist curl (barra)", "sets": 2, "reps": 15},
    {"name": "Reverse wrist curl (barra)", "sets": 2, "reps": 15},
]


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                sort_order INTEGER NOT NULL UNIQUE,
                active INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.commit()


def _insert_exercises(conn, exercises):
    conn.execute("DELETE FROM exercises")
    for idx, ex in enumerate(exercises, start=1):
        conn.execute(
            """
            INSERT INTO exercises (name, sets, reps, sort_order, active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (ex["name"], int(ex["sets"]), int(ex["reps"]), idx),
        )


def list_exercises():
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT name, sets, reps
            FROM exercises
            WHERE active = 1
            ORDER BY sort_order ASC
            """
        ).fetchall()
        return [{"name": r["name"], "sets": r["sets"], "reps": r["reps"]} for r in rows]


def get_or_seed_exercises(seed_exercises=None):
    init_db()
    existing = list_exercises()
    if existing:
        return existing

    to_seed = seed_exercises if seed_exercises else DEFAULT_EXERCISES
    with _connect() as conn:
        _insert_exercises(conn, to_seed)
        conn.commit()
    return list_exercises()


def replace_exercises(exercises):
    init_db()
    with _connect() as conn:
        _insert_exercises(conn, exercises)
        conn.commit()

