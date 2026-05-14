"""Operacoes de treino do IronForge."""

import json
from datetime import date
from pathlib import Path

from . import db_ops

SESSION_FILE = Path(__file__).resolve().parents[1] / "session.json"

TRAINING_EXERCISES = range(0, 13)
TREINO_EXERCISES = TRAINING_EXERCISES
RPE_PROGRESSION_KG = {
    7: 4.0,
    8: 2.0,
    9: 0.0,
    10: -2.0,
}

MUSCLE_MAP = {
    "Agachamento (barra)":             ["Quadriceps", "Gluteos"],
    "Agachamento Zercher":             ["Quadriceps", "Gluteos", "Core"],
    "Zercher squat":                   ["Quadriceps", "Gluteos", "Core"],
    "Levantamento Terra Romeno":       ["Posteriores", "Gluteos"],
    "Supino reto (barra)":             ["Peitoral"],
    "Remada curvada (barra)":          ["Dorsais"],
    "Pullover (barra)":                ["Dorsais"],
    "Desenvolvimento (barra em pé)":   ["Deltoide anterior"],
    "Desenvolvimento (barra em pe)":   ["Deltoide anterior"],
    "Remada alta (barra)":             ["Deltoide lateral", "Trapezio"],
    "Elevação lateral":                ["Deltoide lateral"],
    "Elevacao lateral":                ["Deltoide lateral"],
    "Remada curvada alta no peito (barra)": ["Deltoide posterior", "Trapezio"],
    "Crucifixo invertido":             ["Deltoide posterior"],
    "Rosca direta":                    ["Biceps"],
    "Tríceps testa":                   ["Triceps"],
    "Triceps testa":                   ["Triceps"],
    "Wrist curl (barra)":              ["Antebracos"],
    "Reverse wrist curl (barra)":      ["Antebracos"],
    "Rosca de punho (barra)":          ["Antebracos"],
    "Rosca de punho reversa (barra)":  ["Antebracos"],
    "Encolhimento com barra":          ["Trapezio"],
}


def read_exercises():
    return db_ops.get_or_seed_exercises()


def read_previous_weights():
    return db_ops.get_last_weights()


def read_previous_performance():
    return db_ops.get_last_performance()


def suggest_next_weight(previous_weight, previous_rpe=None):
    if previous_weight is None:
        return None
    if previous_rpe is None:
        return float(previous_weight)

    rpe = int(previous_rpe)
    if rpe <= 7:
        delta = RPE_PROGRESSION_KG[7]
    elif rpe >= 10:
        delta = RPE_PROGRESSION_KG[10]
    else:
        delta = RPE_PROGRESSION_KG.get(rpe, 0.0)
    return float(previous_weight) + delta


def generate_training():
    """
    Cria uma sessao de treino no SQLite.
    Retorna (exercises, session_id), onde exercises e uma lista de
    {log_id, name, sets, reps}.
    """
    all_ex = read_exercises()
    exercises = [all_ex[i] for i in TRAINING_EXERCISES if i < len(all_ex)]
    previous_performance = read_previous_performance()

    today = date.today().strftime("%Y-%m-%d")
    session_id = db_ops.create_session(today)

    session_exercises = []
    for idx, ex in enumerate(exercises):
        log_id = db_ops.log_exercise(session_id, ex["name"], ex["sets"], ex["reps"], idx)
        previous = previous_performance.get(ex["name"], {})
        session_exercises.append({
            "log_id": log_id,
            "name": ex["name"],
            "sets": ex["sets"],
            "reps": ex["reps"],
            "target_weight": suggest_next_weight(previous.get("weight"), previous.get("rpe")),
        })

    return session_exercises, session_id


def gerar_treino():
    return generate_training()


def write_session(exercises, session_id=None):
    data = {
        "date": date.today().strftime("%Y-%m-%d"),
        "exercises": exercises,
    }
    if session_id is not None:
        data["session_id"] = session_id
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
