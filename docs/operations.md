# Operations

This document explains how to run, maintain, and troubleshoot IronForge.

## Daily Use

1. Start the bot.
2. Open Telegram.
3. Send `/generate`.
4. Train.
5. Send weight inputs as you finish exercises.
6. Use `/status` to check progress.
7. Use `/undo` if the last logged exercise was wrong.
8. Stop the bot with `Ctrl+C` when finished.

## Start The Bot

Cross-platform:

```bash
python start_bot.py
```

Linux/macOS if needed:

```bash
python3 start_bot.py
```

Windows wrapper:

```bat
start_bot.bat
```

## First-Time Setup

From the repository root:

```bash
pip install -r requirements.txt
```

Create `.env`:

```bash
copy .env.example .env
```

On Linux/macOS:

```bash
cp .env.example .env
```

Edit `.env` and set:

```text
TELEGRAM_TOKEN=your_real_token
```

Then run:

```bash
python tests/smoke_test.py
python tests/e2e_training_flow_test.py
```

## Bot Commands

```text
/generate     Create a new training session
/exercises    List active exercises
/warmup       Show warmup
/volume       Show muscle volume estimate
/status       Show current progress
/undo         Clear the last logged exercise
/help         Show help
```

Weight input:

```text
80
80 8
80,5
80,5 8
```

## Files To Back Up

Most important:

```text
data/ironforge.db
```

Optional local state:

```text
session.json
```

Secret token:

```text
.env
```

Do not publish `.env`.

## Files That Should Stay Local

These should not be committed:

```text
.env
session.json
pending_log.csv
data/*.db-shm
data/*.db-wal
__pycache__/
*.pyc
```

## Updating Exercises

The exercise catalog lives in SQLite.

Code path:

```text
ironforge/db_ops.py
  -> exercises table
```

Use the existing helpers where possible:

```python
from ironforge import db_ops

db_ops.list_exercises()
db_ops.replace_exercises([...])
```

Do not replace the SQLite exercise source of truth with a spreadsheet.

Current catalog note:

- `Zercher squat` is the first exercise and is programmed as `3x5`.
- It replaced `Agachamento (barra)` for future generated sessions because the
  current setup does not have a proper squat rack.
- Historical `Agachamento (barra)` logs should stay as historical records unless
  a dedicated migration is requested.
- If the catalog changes again, update both `data/ironforge.db` and
  `ironforge/db_ops.py`.

## Common Problems

### `TELEGRAM_TOKEN not found in .env`

Cause:

- missing `.env`
- wrong filename
- missing `TELEGRAM_TOKEN=` line

Fix:

```bash
copy .env.example .env
```

Then edit `.env`.

### Bot starts but ignores messages

Possible causes:

- message is coming from a chat ID different from `CHAT_ID`
- token belongs to a different bot
- Telegram update offset has old updates

Check `CHAT_ID` in:

```text
ironforge/telegram_poller.py
```

### `No active session. Use /generate.`

Cause:

- user sent a weight before generating a session
- `session.json` was deleted

Fix:

```text
/generate
```

### `Old session format. Use /generate...`

Cause:

- `session.json` exists but does not contain `log_id` values
- the file was created by an older version

Fix:

```text
/generate
```

### SQLite database is locked

Possible causes:

- DB Browser for SQLite is open
- another Python process is using the DB
- OneDrive or another sync tool is touching the file

Fix:

1. close DB viewers
2. stop other bot processes
3. pause sync
4. retry

### Raw color codes appear in terminal

Cause:

- terminal does not render ANSI escape codes

Impact:

- cosmetic only
- bot can still run

Fix:

- use Windows Terminal, PowerShell, a modern terminal emulator, or Linux/macOS
  terminal

## Maintenance Checklist

Before pushing a change:

```bash
python tests/smoke_test.py
python tests/e2e_training_flow_test.py
```

For Python syntax checks:

```bash
python -m py_compile start_bot.py ironforge/*.py tests/*.py
```

Before committing:

```bash
git status --short
git diff --check
```

Commit style:

```text
type: short title

Body explaining technical context, scope, and reason.
```

Examples:

```text
feat: add training summary command
fix: preserve rpe when formatting status
refactor: split telegram command handlers
docs: expand system documentation
```
