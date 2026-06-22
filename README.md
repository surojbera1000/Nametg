# Telegram Name-Switcher Bot

A Telegram bot that switches its **public display name** between a "real" name
and a "fake" name using **colourful inline-button callbacks** and the Telegram
Bot API method [`setMyName`](https://core.telegram.org/bots/api#setmyname).

- **No dependencies** — pure Python 3 standard library (long polling).
- **Modular** — each concern lives in its own file.
- Token and names are read from environment variables (never hardcoded).

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
| `config.py` | Settings read from environment variables |
| `telegram_api.py` | Thin Bot API wrapper (`urllib`) |
| `keyboards.py` | Colourful inline keyboards |
| `name_manager.py` | Functions that change/read the bot name |
| `handlers.py` | Message and callback handlers |
| `bot.py` | Polling loop / entry point |

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Configure environment variables (copy `.env.example` to `.env` and edit):

   ```bash
   export TELEGRAM_BOT_TOKEN="123456:ABC-your-token-here"
   export REAL_NAME="My Real Bot"
   export FAKE_NAME="My Fake Bot"
   ```

3. Run it:

   ```bash
   python3 bot.py
   ```

4. In Telegram, open a chat with your bot, send `/start`, and tap the buttons.

## Security

Never commit your bot token. The token is read from `TELEGRAM_BOT_TOKEN`, and
`.env` is git-ignored. If a token is ever exposed, revoke it in @BotFather
(`/revoke`) and generate a new one.

## Important: rate limits

Telegram **limits how often** you can change the bot name (a few times per
hour). Toggling too fast returns HTTP 429 ("Too Many Requests"); the bot shows
"Rate limited by Telegram. Try again in N seconds." instead of crashing. The
name change is **global** (everyone sees it) and may take a moment to propagate
due to client caching.
