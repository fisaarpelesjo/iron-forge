import requests
import json
import time
from pathlib import Path

from . import db_ops
from . import ods_ops

BASE_DIR = Path(__file__).resolve().parents[1]
SESSION_FILE = BASE_DIR / "session.json"
CHAT_ID = "6575275306"


def read_token():
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return None
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and line.split("=", 1)[0].upper() == "TELEGRAM_TOKEN":
                return line.split("=", 1)[1]
    return None


TOKEN = read_token()
API = f"https://api.telegram.org/bot{TOKEN}"


def send(text):
    try:
        requests.post(
            f"{API}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"Send error: {e}")


def load_session():
    if not SESSION_FILE.exists():
        return None
    with open(SESSION_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_updates(offset=0):
    try:
        r = requests.get(
            f"{API}/getUpdates",
            params={"offset": offset, "timeout": 3},
            timeout=10,
        )
        return r.json().get("result", [])
    except Exception:
        return []


def _format_training_msg(exercises):
    prev = db_ops.get_last_weights()
    lines = ["<pre>Training\n"]
    lines.append(f"{'Exercise':<22} {'S':>2} {'R':>3}  {'Kg':>6}\n")
    lines.append("-" * 36 + "\n")
    for ex in exercises:
        kg = prev.get(ex["name"], 0)
        kg_str = "-" if kg == 0 else str(int(kg) if kg == int(kg) else kg)
        lines.append(f"{ex['name'][:22]:<22} {ex['sets']:>2} {ex['reps']:>3}  {kg_str:>6}\n")
    lines.append("</pre>")
    return "".join(lines)


def _format_exercises_msg(exercises):
    lines = ["<pre>Exercise list\n"]
    lines.append(f"{'#':>2} {'Exercise':<22} {'S':>2} {'R':>3}\n")
    lines.append("-" * 34 + "\n")
    for idx, ex in enumerate(exercises, start=1):
        lines.append(f"{idx:>2} {ex['name'][:22]:<22} {ex['sets']:>2} {ex['reps']:>3}\n")
    lines.append("</pre>")
    return "".join(lines)


def handle_generate():
    try:
        exercises, session_id = ods_ops.generate_training()
    except Exception as e:
        send(f"Error generating training session: {e}")
        return

    ods_ops.write_session(exercises, session_id)

    msg = _format_training_msg(exercises)
    send(msg)
    send("Training session generated. Send <code>weight rpe</code> for each exercise.")


def handle(text, session):
    text = text.strip()
    exercises = session.get("exercises", [])

    if not exercises or "log_id" not in exercises[0]:
        send("Old session format. Use /generate to start a new training session.")
        return

    log_ids = [ex["log_id"] for ex in exercises]
    total = len(exercises)
    filled = db_ops.count_filled(log_ids)

    if text.lower() in ("/status", "status"):
        if filled >= total:
            send(f"Training complete. {total}/{total} ✓")
        else:
            ex = exercises[filled]
            done = "\n".join(f"✓ {exercises[i]['name']}" for i in range(filled))
            msg = f"Training — {filled}/{total}\n"
            if done:
                msg += done + "\n"
            msg += f"▶ <b>{ex['name']}</b> ({ex['sets']}x{ex['reps']})"
            send(msg)
        return

    if text.lower() in ("/undo", "undo"):
        if filled == 0:
            send("Nothing to undo.")
            return
        last_ex = exercises[filled - 1]
        db_ops.update_log_weight(last_ex["log_id"], None, None)
        send(f"↩ Undone: <b>{last_ex['name']}</b>")
        return

    if filled >= total:
        send("Training is already complete. Use /status.")
        return

    parts = text.replace(",", ".").split()
    try:
        weight = float(parts[0])
        rpe = int(parts[1]) if len(parts) > 1 else None
    except (ValueError, IndexError):
        send("Format: <code>80 8</code> (weight + RPE) or <code>80</code> (weight only)")
        return

    ex = exercises[filled]
    db_ops.update_log_weight(ex["log_id"], weight, rpe)
    new_filled = filled + 1

    rpe_str = f" RPE {rpe}" if rpe is not None else ""
    if new_filled >= total:
        send(
            f"<b>{ex['name']}</b> ✓ {weight}kg{rpe_str} ({new_filled}/{total})\n\n"
            f"Training complete."
        )
    else:
        nxt = exercises[new_filled]
        send(
            f"<b>{ex['name']}</b> ✓ {weight}kg{rpe_str} ({new_filled}/{total})\n"
            f"▶ {nxt['name']} ({nxt['sets']}x{nxt['reps']})"
        )


def main():
    if not TOKEN:
        print("TELEGRAM_TOKEN not found in .env")
        return

    offset = 0
    print("IronForge bot polling... (Ctrl+C to stop)")

    try:
        while True:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "")

                if chat_id != CHAT_ID or not text:
                    continue

                lower = text.strip().lower()

                if lower in ("/help", "help"):
                    send(
                        "<b>IronForge — Commands</b>\n\n"
                        "/generate — creates a training session\n"
                        "/exercises — lists current exercises\n"
                        "/warmup — shows the warmup list\n"
                        "/volume — sets by muscle group\n"
                        "/status — current exercise and progress\n"
                        "/undo — clears the last logged entry\n"
                        "/help — this message\n\n"
                        "<b>Log weight:</b>\n"
                        "<code>80</code> — weight only\n"
                        "<code>80 8</code> — weight + RPE"
                    )
                    continue

                if lower in ("/exercises", "exercises"):
                    exercises = ods_ops.read_exercises()
                    send(_format_exercises_msg(exercises))
                    continue

                if lower in ("/volume", "volume"):
                    exercises = ods_ops.read_exercises()
                    muscle_sets = {}
                    for ex in exercises:
                        muscles = ods_ops.MUSCLE_MAP.get(ex["name"], ["Other"])
                        for m in muscles:
                            muscle_sets[m] = muscle_sets.get(m, 0) + ex["sets"]
                    lines = ["<b>Volume by muscle</b>\n", "<i>sets/session → sets/week (~3.5x)</i>\n"]
                    for muscle, sets in sorted(muscle_sets.items()):
                        weekly = round(sets * 3.5, 1)
                        lines.append(f"{muscle}: <b>{sets}</b> → ~{weekly:.0f}/sem")
                    send("\n".join(lines))
                    continue

                if lower in ("/warmup", "warmup"):
                    send(
                        "<b>Warmup</b>\n\n"
                        "1. Jump rope or jumping jacks — 3 min\n"
                        "2. Bodyweight squat — 2x10\n"
                        "3. Hip hinge (stiff) — 2x10\n"
                        "4. Arm circles — 15 forward + 15 backward\n"
                        "5. Easy push-up — 1x10\n"
                        "6. Easy row (empty bar or band) — 1x12\n"
                        "7. Empty-bar squat — 1x10\n"
                        "8. Squat ~50% working weight — 1x5\n"
                        "9. Squat ~70% working weight — 1x3\n"
                        "10. Empty-bar bench press — 1x10\n"
                        "11. Bench press ~60% working weight — 1x5\n"
                        "12. Easy overhead press — 1x8"
                    )
                    continue

                if lower.startswith("/generate"):
                    handle_generate()
                    continue

                session = load_session()
                if session is None:
                    send("No active session. Use /generate.")
                    continue

                handle(text, session)

            time.sleep(3)
    except KeyboardInterrupt:
        print("\nBot stopped.")


if __name__ == "__main__":
    main()
