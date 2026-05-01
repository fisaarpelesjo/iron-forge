import requests
import json
import time
from pathlib import Path

import ods_ops

BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "session.json"
PENDING_FILE = BASE_DIR / "pending_log.csv"
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


def load_pending():
    if not PENDING_FILE.exists():
        return []
    entries = []
    with open(PENDING_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            entry = {"row": int(parts[0]), "carga": float(parts[1])}
            if len(parts) > 2 and parts[2]:
                entry["rpe"] = int(parts[2])
            entries.append(entry)
    return entries


def save_pending(entries):
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        for e in entries:
            rpe_str = str(e.get("rpe", ""))
            f.write(f"{e['row']},{e['carga']},{rpe_str}\n")


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


def _format_gerar_msg(treino, exercises):
    prev = ods_ops.read_previous_weights()
    lines = [f"<pre>Treino {treino}\n"]
    lines.append(f"{'Exercicio':<22} {'S':>2} {'R':>3}  {'Kg':>6}\n")
    lines.append("-" * 36 + "\n")
    for ex in exercises:
        kg = prev.get(ex["name"], 0)
        kg_str = "-" if kg == 0 else str(int(kg) if kg == int(kg) else kg)
        lines.append(f"{ex['name'][:22]:<22} {ex['sets']:>2} {ex['reps']:>3}  {kg_str:>6}\n")
    lines.append("</pre>")
    return "".join(lines)


def handle_gerar(treino_type):
    treino_type = treino_type.upper()
    if treino_type not in ("A", "B", "C"):
        send("Treino invalido. Use /gerar A, /gerar B ou /gerar C.")
        return

    if ods_ops.is_ods_locked():
        send("ODS aberto no LibreOffice — feche primeiro.")
        return

    try:
        exercises = ods_ops.gerar_treino(treino_type)
    except Exception as e:
        send(f"Erro ao gerar treino: {e}")
        return

    ods_ops.write_session(treino_type, exercises)
    ods_ops.clear_pending()

    msg = _format_gerar_msg(treino_type, exercises)
    send(msg)
    send(f"Treino {treino_type} gerado! Mande <code>carga rpe</code> para cada exercicio.")


def handle(text, session, pending):
    text = text.strip()
    exercises = session["exercises"]
    treino = session["treino"]
    filled = len(pending)
    total = len(exercises)

    if text.lower() in ("/status", "status"):
        if filled >= total:
            send(f"Treino {treino} completo! {total}/{total} ✓")
        else:
            ex = exercises[filled]
            done = "\n".join(f"✓ {exercises[i]['name']}" for i in range(filled))
            msg = f"Treino {treino} — {filled}/{total}\n"
            if done:
                msg += done + "\n"
            msg += f"▶ <b>{ex['name']}</b> ({ex['sets']}x{ex['reps']})"
            send(msg)
        return

    if text.lower() in ("/undo", "undo"):
        if not pending:
            send("Nada para desfazer.")
            return
        removed = pending.pop()
        ex_name = next((e["name"] for e in exercises if e["row"] == removed["row"]), "?")
        save_pending(pending)
        send(f"↩ Desfeito: <b>{ex_name}</b>")
        return

    if filled >= total:
        send(f"Treino {treino} já completo! Use /status.")
        return

    parts = text.replace(",", ".").split()
    try:
        carga = float(parts[0])
        rpe = int(parts[1]) if len(parts) > 1 else None
    except (ValueError, IndexError):
        send("Formato: <code>80 8</code> (carga + RPE) ou <code>80</code> (só carga)")
        return

    ex = exercises[filled]
    entry = {"row": ex["row"], "carga": carga}
    if rpe is not None:
        entry["rpe"] = rpe

    # Always track in pending (used for filled count / undo)
    pending.append(entry)
    save_pending(pending)

    # Also write directly to ODS if not locked (best-effort; pending is fallback)
    if not ods_ops.is_ods_locked():
        try:
            ods_ops.update_row_weights(ex["row"], carga, rpe)
        except Exception:
            pass

    rpe_str = f" RPE {rpe}" if rpe is not None else ""
    new_filled = len(pending)

    if new_filled >= total:
        send(
            f"<b>{ex['name']}</b> ✓ {carga}kg{rpe_str} ({new_filled}/{total})\n\n"
            f"Treino completo!"
        )
    else:
        nxt = exercises[new_filled]
        send(
            f"<b>{ex['name']}</b> ✓ {carga}kg{rpe_str} ({new_filled}/{total})\n"
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
                        "<b>IronForge — Comandos</b>\n\n"
                        "/gerar A|B|C — gera treino e registra no ODS\n"
                        "/status — exercicio atual e progresso\n"
                        "/undo — desfaz último registro\n"
                        "/help — esta mensagem\n\n"
                        "<b>Registrar peso:</b>\n"
                        "<code>80</code> — só carga\n"
                        "<code>80 8</code> — carga + RPE"
                    )
                    continue

                # /gerar command — no session needed
                if lower.startswith("/gerar"):
                    parts = text.strip().split()
                    treino_arg = parts[1] if len(parts) > 1 else ""
                    handle_gerar(treino_arg)
                    continue

                session = load_session()
                pending = load_pending()

                if session is None:
                    send("Nenhuma sessão ativa. Use /gerar A, /gerar B ou /gerar C.")
                    continue

                handle(text, session, pending)

            time.sleep(3)
    except KeyboardInterrupt:
        print("\nBot encerrado.")


if __name__ == "__main__":
    main()
