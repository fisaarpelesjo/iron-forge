# Portability

IronForge is designed to run on common desktop and server environments.

The core runtime is:

```text
Python 3.10+
SQLite
requests
rich
outbound internet access
```

There is no Docker requirement, no web server requirement, and no database
server requirement.

## Supported Environments

Expected to work:

- Windows
- Linux
- macOS
- WSL
- Raspberry Pi or similar small Linux machines with Python 3.10+
- low-cost VPS
- old laptops that can run modern Python

Not expected to work without extra setup:

- machines without Python 3.10+
- locked-down machines where dependencies cannot be installed
- machines without internet
- mobile OS environments without a real Python runtime
- terminals that cannot render ANSI color correctly

## Python Command Differences

Windows often supports:

```bat
py -3 start_bot.py
python start_bot.py
```

Linux and macOS often use:

```bash
python3 start_bot.py
```

Some systems also map `python` to Python 3:

```bash
python start_bot.py
```

Check with:

```bash
python --version
python3 --version
py -3 --version
```

Use whichever command reports Python 3.10 or newer.

## Dependency Installation

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

If `pip` points to the wrong Python:

```bash
python -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
py -3 -m pip install -r requirements.txt
```

## Windows

Recommended command:

```bat
start_bot.bat
```

or:

```bat
py -3 start_bot.py
```

The batch launcher:

- changes to the project directory
- tries `py -3 start_bot.py`
- falls back to `python start_bot.py`
- shows the process exit code
- pauses before closing

## Linux

Recommended command:

```bash
python3 start_bot.py
```

For a long-running shell session, run it inside `tmux`, `screen`, or a service
manager.

## macOS

Recommended command:

```bash
python3 start_bot.py
```

If Python is missing, install it through python.org, Homebrew, or another
trusted package manager.

## WSL

WSL should behave like Linux.

Use:

```bash
python3 start_bot.py
```

Be careful if the repository is stored under the Windows filesystem and synced
by OneDrive. SQLite locks can be more annoying there.

## Terminal Color

The banner uses `rich`.

If color works, the banner shows fire and metal colors.

If color does not work, the app should still run. Color is cosmetic.

Possible terminal issues:

- old Windows console
- terminal with ANSI disabled
- CI logs that show raw escape codes
- redirected output

The bot does not depend on colored output.

## Weak Machine Requirements

The app is lightweight.

It does:

- simple HTTP requests
- local SQLite reads/writes
- JSON file reads/writes
- periodic sleeps

It does not do:

- video processing
- browser automation at runtime
- heavy machine learning
- web serving
- large batch jobs

The usual bottleneck is not CPU. It is more likely to be:

- internet reliability
- Python installation
- file permissions
- SQLite locks
- synced folders

## OneDrive And Synced Folders

The current workspace path is under OneDrive.

SQLite usually works there, but sync tools can sometimes lock files or create
conflicts.

If database lock issues appear:

1. close DB Browser for SQLite
2. close other Python processes
3. pause OneDrive sync
4. move the repo to a non-synced folder
5. retry the command

## Fresh Machine Checklist

1. Install Python 3.10+.
2. Clone the repository.
3. Enter the repository root.
4. Install dependencies.
5. Create `.env` from `.env.example`.
6. Run smoke test.
7. Run E2E test.
8. Start the bot.

Commands:

```bash
pip install -r requirements.txt
copy .env.example .env
python tests/smoke_test.py
python tests/e2e_training_flow_test.py
python start_bot.py
```

Linux/macOS variant:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 tests/smoke_test.py
python3 tests/e2e_training_flow_test.py
python3 start_bot.py
```
