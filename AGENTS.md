# Codex Instructions For This Repository

## Project Context

This project is a training log with a Telegram bot and a versioned SQLite database.

Main database: `data/ironforge.db`.
Cross-platform launcher: `start_bot.py`.
Windows launcher wrapper: `start_bot.bat`.

## Main Files

Runtime modules live in the `ironforge/` package. Import application modules
from that package, for example `from ironforge import db_ops`.

### `ironforge/telegram_poller.py`

Telegram bot used to control training from the phone.

Supported commands:

- `/generate`
- `/exercises`
- `/warmup`
- `/volume`
- `/status`
- `/undo`
- `/help`
- `80` or `80 8` to log weight and optional RPE

User-facing bot commands and messages must be in English.

Flow:

1. `/generate` creates a training session in SQLite and resets the active session file.
2. Weight input is written directly to SQLite.
3. `/undo` clears the last logged exercise.

### `ironforge/ods_ops.py`

Training-session helper layer.

Key functions:

- `generate_training()` creates a SQLite training session and returns `(exercises, session_id)`.
- `gerar_treino()` is a compatibility alias for older local scripts.
- `read_exercises()` reads from SQLite.
- `read_previous_weights()` returns the latest logged weight by exercise.
- `write_session()` writes `session.json`.

Important rules:

- Active exercise indexes: `TRAINING_EXERCISES = range(0, 13)`.
- Keep `TREINO_EXERCISES` only as a compatibility alias.

### `ironforge/db_ops.py`

SQLite module for exercises, training logs, and diet data.

- Versioned local database: `data/ironforge.db`.
- Main exercise table: `exercises` (`name`, `sets`, `reps`, `sort_order`, `active`).
- The SQLite database is the source of truth for exercises.

## Local State

Local state and secret files are not versioned:

- `session.json`
- `.env` (`TELEGRAM_TOKEN=...`)

Auxiliary SQLite files are not versioned:

- `data/*.db-shm`
- `data/*.db-wal`

Do not version secrets. Before changing local state files, verify that the change is necessary for the task.

## Language Standard

The project interface must be English:

- Telegram commands
- Telegram bot messages
- README usage docs
- launcher messages
- future user-facing text

Historical exercise names stored in SQLite may remain as-is unless the task explicitly includes a data migration.

## Change Guidelines

- Prefer surgical changes compatible with the current flow.
- Keep SQLite as the source of truth for exercises.
- Preserve the distinction between local state and versioned data.
- Prefer existing repository helpers before adding new abstractions.

## Commit Standard

Use Conventional Commits in the commit header:

`feat: add sync command`

Requirements:

- Header must follow `<type>: <title>` (`feat`, `fix`, `refactor`, `chore`, etc.).
- Commit body is required.
- Body must describe technical context, scope, and the reason for the decision.
