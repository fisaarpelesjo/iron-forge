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
├── telegram_poller.py       # Telegram bot long polling
├── ods_ops.py               # Training session operations
├── db_ops.py                # SQLite operations
├── iniciar_bot.bat          # Windows launcher
├── session.json             # Active session state, not versioned
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

## Setup

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install requests
```

3. Create `.env`:

```bash
echo "TELEGRAM_TOKEN=your_token_here" > .env
```

4. Start the bot:

```bash
python telegram_poller.py
```

On Windows, you can also run `iniciar_bot.bat`.

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

`ods_ops.gerar_treino()` is kept as a compatibility alias for older local scripts.
