# Architecture

IronForge is organized as a small Python package with script entry points.

The architecture favors direct, explicit modules instead of a framework. This
keeps the project easy to run on weak machines and easy to debug on Windows,
Linux, macOS, WSL, and small VPS environments.

## Directory Layout

```text
.
├── .env.example
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── requirements.txt
├── start_bot.py
├── start_bot.bat
├── data/
│   └── ironforge.db
├── docs/
├── ironforge/
│   ├── __init__.py
│   ├── banner.py
│   ├── db_ops.py
│   ├── ods_ops.py
│   └── telegram_poller.py
└── tests/
    ├── smoke_test.py
    └── e2e_training_flow_test.py
```

## Import Rules

Application modules should be imported from the package:

```python
from ironforge import db_ops
from ironforge import ods_ops
from ironforge import telegram_poller
from ironforge import banner
```

Do not add new root-level application modules unless they are entry points like
`start_bot.py`.

## Dependency Direction

The intended dependency direction is:

```text
start_bot.py
  -> ironforge.banner
  -> ironforge.telegram_poller
       -> ironforge.ods_ops
       -> ironforge.db_ops
  -> ironforge.ods_ops
       -> ironforge.db_ops
```

`db_ops.py` should stay at the bottom. It should not import the bot layer.

`ods_ops.py` may import `db_ops.py`.

`telegram_poller.py` may import both `ods_ops.py` and `db_ops.py`.

Tests may import all runtime modules.

## Launch Sequence

When `python start_bot.py` runs:

1. Python loads `start_bot.py`.
2. `start_bot.py` imports `ironforge.banner`.
3. `start_bot.py` imports `ironforge.telegram_poller`.
4. `telegram_poller.py` reads `.env` and builds the Telegram API base URL.
5. `start_bot.py` calls `banner.print_banner()`.
6. `start_bot.py` prints `Starting training bot...`.
7. `start_bot.py` calls `telegram_poller.main()`.
8. `telegram_poller.main()` starts long polling.

## Long Polling Model

The bot uses Telegram long polling, not webhooks.

That means:

- No public HTTP server is required.
- No port forwarding is required.
- The bot process periodically calls Telegram `getUpdates`.
- The machine running the bot only needs outbound internet access.

The polling loop sleeps for three seconds between update checks.

## Local State Model

There are three kinds of files:

Versioned project files:

- Python code
- docs
- tests
- `requirements.txt`
- `data/ironforge.db`

Local state files:

- `.env`
- `session.json`
- `pending_log.csv`

Ignored SQLite sidecar files:

- `data/*.db-shm`
- `data/*.db-wal`

Ignored Python cache files:

- `__pycache__/`
- `*.pyc`
- `*.pyo`
- `*.pyd`

## Why `session.json` Exists

The database stores all durable training logs.

The active bot flow still needs to know which session is currently being filled.
That is what `session.json` does.

It contains:

- current date
- current `session_id`
- exercise list
- each exercise `log_id`

The bot uses those `log_id` values to update the right SQLite rows when the
user sends weight input.

## Why The Package Is Named `ironforge`

The app is called IronForge in the README, banner, and database name
`ironforge.db`.

The repository directory has a longer descriptive name, but that name includes
hyphens and Portuguese words. It is not a good Python import namespace.

`ironforge` is short, valid as a Python package name, and aligned with the app
identity.

## Design Constraints

The project should remain:

- easy to run locally
- easy to inspect with SQLite tools
- independent of a web framework
- independent of a server process besides the Telegram poller
- compatible with weak machines
- compatible with Windows, Linux, and macOS

Avoid adding infrastructure unless the project clearly needs it.

## What Not To Do

Do not:

- move exercise source of truth out of SQLite
- version `.env`
- version `session.json`
- version SQLite WAL/SHM sidecar files
- add root-level compatibility wrappers unless explicitly needed
- make Telegram messages Portuguese while the project standard is English
- start using a web server just to receive Telegram messages
- mutate the real database from tests unless the test explicitly says so
