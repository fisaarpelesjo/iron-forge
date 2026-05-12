# Testing

The project has script-based tests under:

```text
tests/
```

They are intentionally plain Python scripts. No pytest dependency is required.

Run tests from the repository root.

## Smoke Test

Command:

```bash
python tests/smoke_test.py
```

On Linux/macOS:

```bash
python3 tests/smoke_test.py
```

Purpose:

- verify Python is at least 3.10
- verify required external dependencies import
- verify runtime modules import
- verify `data/ironforge.db` exists

Modules checked:

```text
requests
rich
ironforge.db_ops
ironforge.ods_ops
ironforge.telegram_poller
ironforge.banner
start_bot
```

Expected output:

```text
Smoke test passed.
```

What it does not prove:

- Telegram token is valid
- Telegram API is reachable
- all bot commands work
- the database has correct content
- terminal color rendering is perfect

## End-To-End Training Flow Test

Command:

```bash
python tests/e2e_training_flow_test.py
```

On Linux/macOS:

```bash
python3 tests/e2e_training_flow_test.py
```

Expected output:

```text
End-to-end training flow test passed.
```

This test exercises the real training flow without using Telegram and without
touching the real database.

It creates:

- temporary SQLite database
- temporary `session.json`
- fake `telegram_poller.send`

Then it runs:

```text
handle_generate()
handle("80 8", session)
handle("/status", session)
handle("/undo", session)
handle("80,5", session)
```

It verifies:

- database is created
- session file is created
- 13 training exercises are generated
- first weight is stored as `80.0`
- first RPE is stored as `8.0`
- status reaches `1/13`
- undo clears weight and RPE
- decimal comma input stores `80.5`

## Why Tests Use Temporary Files

The real files are:

```text
data/ironforge.db
session.json
```

The E2E test should not mutate them.

So it temporarily overrides:

```python
db_ops.DATA_DIR
db_ops.DB_PATH
ods_ops.SESSION_FILE
telegram_poller.SESSION_FILE
telegram_poller.send
```

After the test, it restores all original values.

This gives high confidence in the runtime flow while keeping local training data
safe.

## Test Order

Recommended order on a fresh machine:

```bash
pip install -r requirements.txt
python tests/smoke_test.py
python tests/e2e_training_flow_test.py
```

If smoke fails, fix setup first.

If smoke passes and E2E fails, the environment is probably okay but app behavior
or database logic needs attention.

## Adding More Tests

Prefer tests that:

- use temporary databases
- avoid real Telegram API calls
- avoid mutating `data/ironforge.db`
- avoid mutating real `session.json`
- call existing public functions instead of copying app logic
- assert database state, not only printed messages

Good future tests:

- invalid weight input
- `/undo` when nothing is filled
- completed session behavior
- `/exercises` table formatting
- `/volume` muscle totals
- diet entry totals
- exercise replacement behavior

## Common Test Failures

`ModuleNotFoundError: requests`

Run:

```bash
pip install -r requirements.txt
```

`Missing database: data/ironforge.db`

Make sure the repository includes `data/ironforge.db` and that you are running
the command from the repository root.

SQLite permission or lock error:

- close DB Browser for SQLite
- close other scripts using the database
- avoid running the project from a synced folder if locks repeat

Wrong working directory:

Run tests from the repository root, not from inside `tests/`.

## Manual Verification

To manually verify the bot without running forever:

1. run smoke test
2. run E2E test
3. confirm `.env` exists
4. start the bot
5. send `/help`
6. send `/generate`
7. send `80 8`
8. send `/status`
9. send `/undo`

Stop the bot with `Ctrl+C`.
