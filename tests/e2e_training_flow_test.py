import gc
import json
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ironforge import db_ops
from ironforge import ods_ops
from ironforge import telegram_poller


def _fetch_log(db_path, log_id):
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT exercise_name, weight, rpe
            FROM training_logs
            WHERE id = ?
            """,
            (log_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def main():
    original_db_path = db_ops.DB_PATH
    original_data_dir = db_ops.DATA_DIR
    original_ods_session = ods_ops.SESSION_FILE
    original_poller_session = telegram_poller.SESSION_FILE
    original_send = telegram_poller.send

    sent_messages = []

    with tempfile.TemporaryDirectory(prefix="ironforge-e2e-") as temp_dir:
        temp_path = Path(temp_dir)
        test_db = temp_path / "ironforge.db"
        test_session = temp_path / "session.json"

        try:
            db_ops.DATA_DIR = temp_path
            db_ops.DB_PATH = test_db
            ods_ops.SESSION_FILE = test_session
            telegram_poller.SESSION_FILE = test_session
            telegram_poller.send = sent_messages.append

            telegram_poller.handle_generate()
            assert test_db.exists(), "E2E database was not created."
            assert test_session.exists(), "E2E session file was not created."

            session = json.loads(test_session.read_text(encoding="utf-8"))
            exercises = session["exercises"]
            assert len(exercises) == len(list(ods_ops.TRAINING_EXERCISES))
            assert "Training session generated." in sent_messages[-1]

            first_log_id = exercises[0]["log_id"]

            telegram_poller.handle("80 8", session)
            first_log = _fetch_log(test_db, first_log_id)
            assert first_log["weight"] == 80.0
            assert first_log["rpe"] == 8.0
            assert "80.0kg RPE 8" in sent_messages[-1]

            telegram_poller.handle("/status", session)
            assert "Training" in sent_messages[-1]
            assert "1/13" in sent_messages[-1]

            telegram_poller.handle("/undo", session)
            undone_log = _fetch_log(test_db, first_log_id)
            assert undone_log["weight"] is None
            assert undone_log["rpe"] is None
            assert "Undone" in sent_messages[-1]

            telegram_poller.handle("80,5", session)
            relogged = _fetch_log(test_db, first_log_id)
            assert relogged["weight"] == 80.5
            assert relogged["rpe"] is None

            print("End-to-end training flow test passed.")
        finally:
            db_ops.DB_PATH = original_db_path
            db_ops.DATA_DIR = original_data_dir
            ods_ops.SESSION_FILE = original_ods_session
            telegram_poller.SESSION_FILE = original_poller_session
            telegram_poller.send = original_send
            gc.collect()


if __name__ == "__main__":
    main()
