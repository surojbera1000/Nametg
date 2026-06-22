# Telegram Name-Switcher Bot

A Telegram bot that switches its **public display name** between a "real" name
and a "fake" name using **colourful inline-button callbacks** and the Telegram
Bot API method [`setMyName`](https://core.telegram.org/bots/api#setmyname).

- **No dependencies** — pure Python 3 standard library (long polling).
- **Modular** — each concern lives in its own file.
- **One place to configure** — a single `.env` file in this folder. No `export` needed.

## Buttons

```
[ 🟢 Real Name ] [ 🔴 Fake Name ]
[ 🔵 Show Current Name ]
```

Tapping a button sends a **callback query**; the bot answers it and calls
`setMyName` (or `getMyName` for "Show Current Name").

> Note: Telegram doesn't allow bots to set custom button background colours, so
> the buttons are made colourful with emoji icons that render in colour on all
> clients.

## Project structure

| File | Responsibility |
|------|----------------|
| `config.py` | Settings; auto-loads `.env` from this folder |
| `telegram_api.py` | Thin Bot API wrapper (`urllib`) |
| `keyboards.py` | Colourful inline keyboards |
| `name_manager.py` | Functions that change/read the bot name |
| `handlers.py` | Message and callback handlers |
| `bot.py` | Polling loop / entry point |
| `tests/test_bot.py` | Automated tests (mock the API, no internet needed) |

## Tests

The logic is covered by an automated test suite that mocks the Telegram API, so
it runs anywhere without a token or internet:

```bash
python3 -m unittest discover -s tests -v
```

## Setup (only ONE place to configure)

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. In this folder, copy `.env.example` to `.env` and put your token in it:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-your-token-here
   REAL_NAME=My Real Bot
   FAKE_NAME=My Fake Bot
   ```

3. Run it — **no `export` needed anywhere**, the bot loads `.env` automatically:

   ```bash
   python3 bot.py
   ```

4. In Telegram, open a chat with your bot, send `/start`, and tap the buttons.

### Running on a VPS (keep it alive)

The `.env` file is the only thing you configure. To keep the bot running after
you log out, use one of these:

```bash
# simplest: run in background, logs to bot.log
nohup python3 bot.py > bot.log 2>&1 &
```

Or with `screen` / `tmux`:

```bash
screen -S nametg
python3 bot.py
# press Ctrl+A then D to detach; `screen -r nametg` to return
```

## Security

Never commit your bot token. It lives only in your local `.env` file, which is
git-ignored and never pushed. If a token is ever exposed, revoke it in
@BotFather (`/revoke`) and generate a new one.

## Important: rate limits

Telegram **limits how often** you can change the bot name (a few times per
hour). Toggling too fast returns HTTP 429 ("Too Many Requests"); the bot shows
"Rate limited by Telegram. Try again in N seconds." instead of crashing. The
name change is **global** (everyone sees it) and may take a moment to propagate
due to client caching.
