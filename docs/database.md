# Database

IronForge uses SQLite.

The main database file is:

```text
data/ironforge.db
```

This database is versioned in Git. It is the source of truth for exercises,
training sessions, training logs, foods, diet entries, and diet targets.

## SQLite Module

All direct database access belongs in:

```text
ironforge/db_ops.py
```

The module defines:

```python
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "ironforge.db"
```

Because `db_ops.py` lives inside the `ironforge/` package, `parents[1]` resolves
to the repository root. The database path remains `data/ironforge.db`.

## Connection Behavior

The private `_connect()` helper:

- creates `DATA_DIR` if missing
- connects to `DB_PATH`
- sets `row_factory = sqlite3.Row`
- enables foreign keys with `PRAGMA foreign_keys = ON`

`sqlite3.Row` allows rows to be accessed by column name.

Foreign keys are enabled per connection because SQLite requires that setting on
each new connection.

## Initialization

`init_db()` creates all tables if they do not already exist.

It is safe to call repeatedly. It uses `CREATE TABLE IF NOT EXISTS`.

Several public functions call `init_db()` before reading or writing.

## Tables

### `exercises`

Stores the exercise catalog.

Columns:

```text
id          INTEGER PRIMARY KEY AUTOINCREMENT
name        TEXT NOT NULL UNIQUE
sets        INTEGER NOT NULL
reps        INTEGER NOT NULL
sort_order  INTEGER NOT NULL UNIQUE
active      INTEGER NOT NULL DEFAULT 1
```

Rules:

- `name` is unique.
- `sort_order` determines display and training order.
- only rows with `active = 1` are used by `list_exercises()`.
- this table is the exercise source of truth.

### `training_sessions`

Stores one row per generated training session.

Columns:

```text
id             INTEGER PRIMARY KEY AUTOINCREMENT
date           TEXT NOT NULL
training_type  TEXT NOT NULL DEFAULT 'TREINO'
```

`date` is stored as an ISO-style string, currently `YYYY-MM-DD`.

### `training_logs`

Stores one row per exercise inside a training session.

Columns:

```text
id             INTEGER PRIMARY KEY AUTOINCREMENT
session_id     INTEGER NOT NULL REFERENCES training_sessions(id)
exercise_name  TEXT NOT NULL
sets           INTEGER NOT NULL
reps           INTEGER NOT NULL
weight         REAL
rpe            REAL
sort_order     INTEGER NOT NULL DEFAULT 0
```

Rows are created during `/generate`.

`weight` and `rpe` start as `NULL`.

When the user sends `80` or `80 8`, `weight` and optional `rpe` are written to
the next unfilled row.

`/undo` sets both back to `NULL` for the last filled row in the active session.

### `foods`

Stores food definitions for diet tracking.

Columns:

```text
id             INTEGER PRIMARY KEY AUTOINCREMENT
name           TEXT NOT NULL UNIQUE
unit           TEXT NOT NULL
serving_g      REAL NOT NULL DEFAULT 100
protein_g      REAL NOT NULL DEFAULT 0
carbo_g        REAL NOT NULL DEFAULT 0
fat_g          REAL NOT NULL DEFAULT 0
calories       REAL NOT NULL DEFAULT 0
fiber_g        REAL NOT NULL DEFAULT 0
omega3_g       REAL NOT NULL DEFAULT 0
potassium_mg   REAL NOT NULL DEFAULT 0
magnesium_mg   REAL NOT NULL DEFAULT 0
zinc_mg        REAL NOT NULL DEFAULT 0
vitamin_d_ui   REAL NOT NULL DEFAULT 0
```

`upsert_food()` inserts or updates by unique `name`.

### `diet_targets`

Stores current diet targets.

Columns:

```text
id             INTEGER PRIMARY KEY AUTOINCREMENT
protein_g      REAL
carbo_g        REAL
fat_g          REAL
calories       REAL
fiber_g        REAL
omega3_g       REAL
potassium_mg   REAL
magnesium_mg   REAL
zinc_mg        REAL
vitamin_d_ui   REAL
```

`set_diet_targets()` deletes existing rows and inserts one new target row.

### `diet_entries`

Stores consumed food entries.

Columns:

```text
id          INTEGER PRIMARY KEY AUTOINCREMENT
meal        TEXT NOT NULL
food_id     INTEGER NOT NULL REFERENCES foods(id)
quantity    REAL NOT NULL
sort_order  INTEGER NOT NULL DEFAULT 0
```

Diet totals are computed by joining `diet_entries` with `foods`.

## Exercise Seeding

`DEFAULT_EXERCISES` contains the fallback exercise list.

`get_or_seed_exercises()` works like this:

1. call `init_db()`
2. call `list_exercises()`
3. if active exercises exist, return them
4. otherwise insert `DEFAULT_EXERCISES`
5. return the inserted exercise list

This means the default list is only used when the database has no active
exercises.

## Current First Exercise

The current active exercise catalog starts with:

```text
sort_order 1
name       Zercher squat
sets       3
reps       5
```

`Zercher squat` replaced `Agachamento (barra)` for future generated sessions
because the user does not have a proper squat rack. Historical training logs
with `exercise_name = 'Agachamento (barra)'` should remain unchanged unless a
task explicitly asks for a historical migration.

When changing the active catalog for future sessions, update both:

- `data/ironforge.db`, because SQLite is the active source of truth
- `ironforge/db_ops.py`, because `DEFAULT_EXERCISES` seeds fresh databases

## Training Session Creation

`ods_ops.generate_training()` creates a session through `db_ops`.

Flow:

```text
ods_ops.generate_training()
  -> ods_ops.read_exercises()
     -> db_ops.get_or_seed_exercises()
  -> select indexes TRAINING_EXERCISES = range(0, 13)
  -> db_ops.create_session(today)
  -> db_ops.log_exercise(...) for each selected exercise
  -> return (session_exercises, session_id)
```

The returned `session_exercises` list contains dictionaries like:

```python
{
    "log_id": 123,
    "name": "Zercher squat",
    "sets": 3,
    "reps": 5,
}
```

Those `log_id` values are what connect Telegram weight input to SQLite rows.

## Counting Progress

`count_filled(log_ids)` counts how many active-session log rows already have
`weight IS NOT NULL`.

The bot uses this count as the index of the next exercise.

Example:

```text
filled = 0 -> next exercise is exercises[0]
filled = 1 -> next exercise is exercises[1]
filled = 13 -> training is complete
```

## Latest Weights

`get_last_weights()` returns:

```python
{
    "Exercise name": latest_weight,
}
```

It uses the latest row ID per exercise where `weight IS NOT NULL AND weight > 0`.

This is used when formatting the training table after `/generate`.

## Safe Inspection Commands

From the repository root:

```bash
sqlite3 data/ironforge.db ".tables"
sqlite3 data/ironforge.db ".schema exercises"
sqlite3 data/ironforge.db "SELECT name, sets, reps FROM exercises ORDER BY sort_order;"
sqlite3 data/ironforge.db "SELECT * FROM training_sessions ORDER BY id DESC LIMIT 5;"
```

On Windows, if `sqlite3` is not installed, use DB Browser for SQLite or install
SQLite command-line tools.

## Files Not To Version

Do not commit:

```text
data/*.db-shm
data/*.db-wal
session.json
.env
```

WAL and SHM files are SQLite runtime sidecars. They are not the durable project
database.

## Test Isolation

`tests/e2e_training_flow_test.py` does not use `data/ironforge.db`.

It temporarily points:

- `db_ops.DATA_DIR`
- `db_ops.DB_PATH`
- `ods_ops.SESSION_FILE`
- `telegram_poller.SESSION_FILE`

to temporary files under the OS temp directory.

This protects the real database and real active session while still testing the
same runtime functions.
