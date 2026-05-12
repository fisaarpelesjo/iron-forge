# Repository Notes

IronForge is a training log with a Telegram bot and SQLite storage.

## Core Modules

### `telegram_poller.py`

Telegram long-polling bot.

Commands:

- `/generate` creates a SQLite training session and sends the exercise table.
- `/exercises` lists current exercises.
- `/warmup` shows the warmup protocol.
- `/volume` shows sets by muscle group.
- `/status` shows active-session progress.
- `/undo` clears the last logged exercise.
- `/help` lists commands.
- `80` or `80 8` logs weight and optional RPE.

All user-facing commands and bot messages should be English.

### `ods_ops.py`

Training operation helpers:

- `generate_training()` creates a session and training log rows in SQLite.
- `gerar_treino()` remains as a compatibility alias.
- `read_exercises()` reads exercises from SQLite.
- `read_previous_weights()` returns latest weights from SQLite.
- `write_session()` writes active session state to `session.json`.

### `db_ops.py`

SQLite operations:

- `get_or_seed_exercises()`
- `list_exercises()`
- `create_session()`
- `log_exercise()`
- `update_log_weight()`
- `get_last_weights()`
- `count_filled()`

## Data And State

- Versioned database: `data/ironforge.db`.
- Local state: `session.json`, not versioned.
- Secret config: `.env`, not versioned.
- SQLite sidecar files (`*.db-shm`, `*.db-wal`) are not versioned.

The SQLite database is the source of truth for exercises. Do not move exercise management back to an ODS sheet.

## Commit Style

Use Conventional Commits:

```text
feat: add sync command

Explain the technical context, scope, and reason for the change.
```
