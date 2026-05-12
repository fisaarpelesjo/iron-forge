# System Overview

IronForge is a small training log controlled from Telegram.

The project has three core responsibilities:

1. Keep a versioned local SQLite database at `data/ironforge.db`.
2. Run a Telegram long-polling bot that accepts training commands from a phone.
3. Store the currently active training session in local state at `session.json`.

The project is intentionally simple. There is no web server, no container
runtime, no background queue, and no external database server. The runtime is
Python plus SQLite plus the Telegram HTTP API.

## Main User Flow

The normal workout flow is:

```text
User sends /generate in Telegram
  -> bot creates a training session in SQLite
  -> bot creates one training log row per active exercise
  -> bot writes session.json with the active exercise list and log IDs
  -> bot sends the exercise table back to Telegram

User sends 80 or 80 8
  -> bot loads session.json
  -> bot counts filled log rows in SQLite
  -> bot finds the next unfilled exercise
  -> bot writes weight and optional RPE into SQLite
  -> bot replies with progress and next exercise

User sends /undo
  -> bot loads session.json
  -> bot counts filled log rows in SQLite
  -> bot clears the most recent filled log row
  -> bot replies with the undone exercise
```

## Runtime Entry Points

Use these commands from the repository root.

```bash
python start_bot.py
```

This is the cross-platform launcher. It prints the terminal banner and starts
the Telegram polling loop.

On Windows, this also works:

```bat
start_bot.bat
```

The batch file is only a Windows wrapper. It delegates to `start_bot.py`.

## Package Layout

Application code lives in the `ironforge/` Python package:

```text
ironforge/
├── __init__.py
├── banner.py
├── db_ops.py
├── ods_ops.py
└── telegram_poller.py
```

Test scripts live in `tests/`:

```text
tests/
├── smoke_test.py
└── e2e_training_flow_test.py
```

Documentation lives in `docs/`.

Versioned data lives in `data/`.

Local state and secrets stay at the repository root but are not versioned:

```text
.env
session.json
pending_log.csv
```

## Responsibilities By File

`start_bot.py`

- Cross-platform launcher.
- Imports `ironforge.banner`.
- Imports `ironforge.telegram_poller`.
- Prints the banner.
- Starts the bot by calling `telegram_poller.main()`.

`start_bot.bat`

- Windows-only wrapper.
- Changes into the repository directory.
- Runs `py -3 start_bot.py`.
- Falls back to `python start_bot.py` if the Python launcher is not available.
- Prints the exit code when the bot stops.

`ironforge/banner.py`

- Owns the terminal ASCII banner.
- Uses `rich` for color when available.
- Falls back to plain text if `rich` cannot be imported.
- Does not start the bot.

`ironforge/telegram_poller.py`

- Owns Telegram communication.
- Reads `TELEGRAM_TOKEN` from `.env`.
- Polls `getUpdates`.
- Sends messages through `sendMessage`.
- Parses Telegram commands and weight inputs.
- Uses `ods_ops` and `db_ops` for training state and persistence.

`ironforge/ods_ops.py`

- Owns training-session helper behavior.
- Reads active exercises from SQLite through `db_ops`.
- Creates a training session.
- Creates one training log row per active exercise.
- Writes `session.json`.
- Keeps `gerar_treino()` as a compatibility alias.

`ironforge/db_ops.py`

- Owns SQLite access.
- Creates tables if missing.
- Reads and writes exercises.
- Creates training sessions.
- Creates and updates training logs.
- Stores diet foods, diet entries, and diet targets.

`tests/smoke_test.py`

- Checks that the local environment is minimally usable.
- Verifies Python version, imports, dependencies, and database presence.

`tests/e2e_training_flow_test.py`

- Runs an isolated local training flow.
- Uses a temporary SQLite database and temporary `session.json`.
- Does not call Telegram.
- Does not mutate `data/ironforge.db`.

## Source Of Truth

SQLite is the source of truth for exercises and logs.

`session.json` is not the source of truth. It is only the active-session pointer
used by the bot to know which log IDs belong to the current workout.

The exercise catalog should not be moved back to ODS or spreadsheet files.

## Current Training Catalog Note

The first active exercise is currently:

```text
Zercher squat - 3x5
```

It replaced `Agachamento (barra)` for future generated sessions because the
current home gym setup does not have a proper squat rack. The change is a
forward-looking catalog update. Historical `Agachamento (barra)` logs remain
valid historical records.

## User-Facing Language

All user-facing project interface text should be English:

- Telegram commands
- Telegram bot messages
- README usage instructions
- launcher messages
- future user-visible text

Historical exercise names already stored in SQLite may remain as-is unless a
task explicitly asks for a data migration.
