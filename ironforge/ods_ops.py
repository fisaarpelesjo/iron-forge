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

REST_INTERVALS = {
    "Agachamento Zercher": "3-5 min",
    "Supino reto (barra)": "3-5 min",
    "Remada curvada (barra)": "2-4 min",
    "Desenvolvimento (barra em pé)": "2-4 min",
    "Desenvolvimento (barra em pe)": "2-4 min",
    "Levantamento Terra Romeno": "3-5 min",
    "Pullover (barra)": "90-150 s",
    "Remada alta (barra)": "90-150 s",
    "Remada curvada alta no peito (barra)": "90-150 s",
    "Encolhimento com barra": "90-150 s",
    "Rosca direta": "60-120 s",
    "Tríceps testa": "60-120 s",
    "Triceps testa": "60-120 s",
    "Rosca de punho (barra)": "45-90 s",
    "Rosca de punho reversa (barra)": "45-90 s",
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


def get_rest_interval(exercise_name):
    return REST_INTERVALS.get(exercise_name, "2-3 min")


def build_training_plan(persist=True):
    """
    Monta o treino atual com carga alvo e descanso.
    Se persist=True, cria sessao e logs no SQLite.
    """
    all_ex = read_exercises()
    exercises = [all_ex[i] for i in TRAINING_EXERCISES if i < len(all_ex)]
    previous_performance = read_previous_performance()

    session_id = None
    if persist:
        today = date.today().strftime("%Y-%m-%d")
        session_id = db_ops.create_session(today)

    session_exercises = []
    for idx, ex in enumerate(exercises):
        log_id = None
        if persist:
            log_id = db_ops.log_exercise(session_id, ex["name"], ex["sets"], ex["reps"], idx)
        previous = previous_performance.get(ex["name"], {})
        item = {
            "name": ex["name"],
            "sets": ex["sets"],
            "reps": ex["reps"],
            "target_weight": suggest_next_weight(previous.get("weight"), previous.get("rpe")),
            "rest_interval": get_rest_interval(ex["name"]),
        }
        if log_id is not None:
            item["log_id"] = log_id
        session_exercises.append(item)

    return session_exercises, session_id


def generate_training():
    """
    Cria uma sessao de treino no SQLite.
    Retorna (exercises, session_id), onde exercises e uma lista de
    {log_id, name, sets, reps}.
    """
    return build_training_plan(persist=True)


def preview_training():
    return build_training_plan(persist=False)[0]


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
