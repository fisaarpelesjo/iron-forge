# Telegram Bot

The Telegram bot lives in:

```text
ironforge/telegram_poller.py
```

It uses Telegram long polling through the HTTP API.

## Configuration

The bot reads the token from:

```text
.env
```

Expected format:

```text
TELEGRAM_TOKEN=your_token_here
```

The parser is intentionally small:

- opens `.env`
- strips each line
- looks for a key named `TELEGRAM_TOKEN`
- returns the value after the first `=`

The current chat allowlist is stored in code as:

```python
CHAT_ID = "6575275306"
```

Only messages from this chat ID are handled.

## Startup

The normal startup path is:

```text
start_bot.py
  -> banner.print_banner()
  -> telegram_poller.main()
```

If the token is missing, `main()` prints:

```text
TELEGRAM_TOKEN not found in .env
```

and returns without polling.

## Polling Loop

`main()` starts with:

```python
offset = 0
```

Then it loops forever:

1. call `get_updates(offset)`
2. iterate returned updates
3. update `offset` to `update_id + 1`
4. ignore messages from any chat other than `CHAT_ID`
5. ignore updates without text
6. dispatch commands or weight input
7. sleep for 3 seconds

`KeyboardInterrupt` prints:

```text
Bot stopped.
```

## Telegram API Calls

`get_updates(offset)` calls:

```text
GET https://api.telegram.org/bot<TOKEN>/getUpdates
```

Parameters:

```python
{
    "offset": offset,
    "timeout": 3,
}
```

`send(text)` calls:

```text
POST https://api.telegram.org/bot<TOKEN>/sendMessage
```

JSON body:

```python
{
    "chat_id": CHAT_ID,
    "text": text,
    "parse_mode": "HTML",
}
```

Messages may use Telegram HTML formatting such as:

- `<b>bold</b>`
- `<i>italic</i>`
- `<code>monospace</code>`
- `<pre>preformatted</pre>`

## Commands

### `/help`

Shows command list and weight logging examples.

Also accepts:

```text
help
```

### `/generate`

Creates a new training session.

The current first generated exercise is `Zercher squat` (`3x5`), because it
replaced `Agachamento (barra)` in the active SQLite exercise catalog.

Flow:

```text
handle_generate()
  -> ods_ops.generate_training()
  -> ods_ops.write_session(exercises, session_id)
  -> _format_training_msg(exercises)
  -> send(training table)
  -> send("Training session generated...")
```

This command writes to:

- `data/ironforge.db`
- `session.json`

### `/exercises`

Reads active exercises from SQLite and sends a compact table.

Also accepts:

```text
exercises
```

### `/warmup`

Sends the hardcoded warmup protocol.

The warmup is intentionally compact because the full workout already takes about
two hours. The exercise names in this list use PT-BR local training terminology,
while the command itself remains `/warmup`. It avoids prescribed warmup loads and
uses simple "barra vazia" or "leve" cues instead.

Also accepts:

```text
warmup
```

### `/volume`

Reads active exercises, maps each exercise to muscles through
`ods_ops.MUSCLE_MAP`, then sends estimated volume.

The weekly estimate is:

```python
weekly = round(sets * 3.5, 1)
```

Also accepts:

```text
volume
```

### `/status`

Loads the active session and counts filled logs.

If all logs are filled, it sends:

```text
Training complete. total/total
```

Otherwise it sends:

- current progress
- completed exercises
- current exercise

Also accepts:

```text
status
```

### `/undo`

Clears the last filled exercise in the active session.

Flow:

```text
load active session
count filled log rows
if filled == 0 -> send "Nothing to undo."
else -> update latest filled log row weight=NULL and rpe=NULL
```

Also accepts:

```text
undo
```

## Weight Input

Supported examples:

```text
80
80 8
80,5
80,5 8
```

Parsing rules:

1. replace comma with dot
2. split on whitespace
3. parse first part as `float`
4. parse second part as `int` if present

Invalid input receives:

```text
Format: 80 8 (weight + RPE) or 80 (weight only)
```

## Active Session Format

`session.json` must contain:

```json
{
  "date": "YYYY-MM-DD",
  "session_id": 1,
  "exercises": [
    {
      "log_id": 1,
      "name": "Zercher squat",
      "sets": 3,
      "reps": 5
    }
  ]
}
```

If the session is missing or old-format, the bot asks the user to run
`/generate`.

## Important Failure Modes

Missing `.env`:

- bot prints a local error and does not poll

Wrong Telegram token:

- API calls fail
- send errors may be printed locally

Wrong chat ID:

- bot receives updates but ignores them

Missing `session.json`:

- weight input sends `No active session. Use /generate.`

Old `session.json` format:

- bot sends `Old session format. Use /generate to start a new training session.`

SQLite locked:

- usually caused by another process holding the database file
- more likely in synced folders such as OneDrive
- close SQLite viewers and retry

## Safety Rule

The bot never trusts Telegram input to directly choose a database row.

It uses the active `session.json` log IDs and the count of filled rows to choose
the next exercise.
