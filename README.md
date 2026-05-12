# IronForge

Training and diet log with a Telegram bot and a local SQLite database.

## Overview

IronForge lets you control a training session from Telegram:

- `/generate` creates a new training session in SQLite.
- Sending `80` logs 80 kg for the next pending exercise.
- Sending `80 8` logs 80 kg with RPE 8.
- `/status` shows progress in the active session.
- `/undo` clears the last logged exercise.

The main local database is `data/ironforge.db`. The active Telegram session is stored in `session.json`, which is intentionally not versioned.

## Files

```text
ironforge/
├── start_bot.py             # Cross-platform launcher
├── start_bot.bat            # Windows launcher wrapper
├── ironforge/
│   ├── banner.py            # Terminal banner
│   ├── telegram_poller.py   # Telegram bot long polling
│   ├── ods_ops.py           # Training session operations
│   └── db_ops.py            # SQLite operations
├── tests/
│   ├── smoke_test.py        # Local setup check
│   └── e2e_training_flow_test.py # Local end-to-end flow test
├── session.json             # Active session state, not versioned
├── .env.example             # Environment template
├── .env                     # TELEGRAM_TOKEN=..., not versioned
└── data/
    └── ironforge.db         # Versioned SQLite database
```

## Telegram Commands

```text
/generate     Create a SQLite training session and show the exercise table
/exercises    List the current exercises, sets, reps, and last weights
/warmup       Show the recommended warmup
/volume       Show sets by muscle group and weekly estimate
/status       Show current exercise and session progress
/undo         Clear the last logged exercise
/help         Show command help
```

## Logging Weights

```text
80        Log 80 kg for the next pending exercise
80 8      Log 80 kg and RPE 8
80,5 8    Decimal comma is accepted and stored as 80.5 kg
```

## Training Flow

```text
/generate
  -> db_ops.get_or_seed_exercises()
  -> db_ops.create_session(date)
  -> db_ops.log_exercise(...) for each active exercise
  -> ods_ops.write_session(...) writes session.json

"80 8"
  -> load active session
  -> find the next exercise without weight
  -> db_ops.update_log_weight(log_id, 80.0, 8)

/undo
  -> find the last filled exercise
  -> db_ops.update_log_weight(log_id, None, None)
```

## Current Training Catalog

The active catalog starts with:

```text
Zercher squat    3x5
```

`Zercher squat` replaced `Agachamento (barra)` for future generated sessions
because the current home setup does not have a proper squat rack. Historical
`Agachamento (barra)` logs remain historical data and do not need to be renamed.

## Setup

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env`:

```bash
echo "TELEGRAM_TOKEN=your_token_here" > .env
```

4. Check the setup:

```bash
python tests/smoke_test.py
```

5. Run the local end-to-end test:

```bash
python tests/e2e_training_flow_test.py
```

6. Start the bot:

```bash
python start_bot.py
```

On Linux and macOS, use `python3 start_bot.py` if `python` points to Python 2.
On Windows, you can also run `start_bot.bat`.

## Database

Main tables:

- `exercises`
- `training_sessions`
- `training_logs`
- `foods`
- `diet_targets`
- `diet_entries`

The exercise catalog is stored in SQLite. Do not replace it with an ODS sheet.

## Internal API

```python
db_ops.get_or_seed_exercises()
db_ops.create_session(date_iso, training_type="TREINO")
db_ops.log_exercise(session_id, name, sets, reps, sort_order)
db_ops.update_log_weight(log_id, weight, rpe=None)
db_ops.get_last_weights()
db_ops.count_filled(log_ids)

ods_ops.generate_training()
ods_ops.write_session(exercises, session_id)
ods_ops.read_exercises()
ods_ops.read_previous_weights()
```

Import these APIs from the package, for example `from ironforge import db_ops`.
`ironforge.ods_ops.gerar_treino()` is kept as a compatibility alias for older local scripts.

## Detailed Documentation

Detailed project documentation is in [`docs/index.md`](docs/index.md):

- architecture and module boundaries
- SQLite schema and source-of-truth rules
- Telegram command flow
- smoke and end-to-end tests
- portability across Windows, Linux, macOS, and weak machines
- operations and troubleshooting
