"""Training operations for IronForge."""

import json
from datetime import date
from pathlib import Path

import db_ops

SESSION_FILE = Path(__file__).parent / "session.json"

TREINO_EXERCISES = range(0, 13)

MUSCLE_MAP = {
    "Agachamento (barra)":             ["Quadriceps", "Gluteos"],
    "Stiff com barra":                 ["Isquiotibiais", "Gluteos"],
    "Supino reto (barra)":             ["Peitoral"],
    "Remada curvada (barra)":          ["Dorsais"],
    "Pullover (barra)":                ["Dorsais"],
    "Desenvolvimento (barra em pé)":   ["Deltóide anterior"],
    "Desenvolvimento (barra em pe)":   ["Deltóide anterior"],
    "Remada alta (barra)":             ["Deltóide lateral", "Trapezio"],
    "Elevação lateral":                ["Deltóide lateral"],
    "Elevacao lateral":                ["Deltóide lateral"],
    "Remada curvada aberta (barra)":   ["Deltóide posterior", "Trapezio"],
    "Crucifixo invertido":             ["Deltóide posterior"],
    "Rosca direta":                    ["Biceps"],
    "Tríceps testa":                   ["Triceps"],
    "Triceps testa":                   ["Triceps"],
    "Wrist curl (barra)":              ["Antebraco"],
    "Reverse wrist curl (barra)":      ["Antebraco"],
    "Encolhimento com barra":          ["Trapezio"],
}


def read_exercises():
    return db_ops.get_or_seed_exercises()


def read_previous_weights():
    return db_ops.get_last_weights()


def gerar_treino():
    """
    Create training session in SQLite.
    Returns (exercises, session_id) where exercises is list of
    {log_id, name, sets, reps}.
    """
    all_ex = read_exercises()
    exercises = [all_ex[i] for i in TREINO_EXERCISES if i < len(all_ex)]

    today = date.today().strftime("%Y-%m-%d")
    session_id = db_ops.create_session(today)

    session_exercises = []
    for idx, ex in enumerate(exercises):
        log_id = db_ops.log_exercise(session_id, ex["name"], ex["sets"], ex["reps"], idx)
        session_exercises.append({
            "log_id": log_id,
            "name": ex["name"],
            "sets": ex["sets"],
            "reps": ex["reps"],
        })

    return session_exercises, session_id


def write_session(exercises, session_id=None):
    data = {
        "date": date.today().strftime("%Y-%m-%d"),
        "exercises": exercises,
    }
    if session_id is not None:
        data["session_id"] = session_id
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
