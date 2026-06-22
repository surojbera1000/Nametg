# Telegram Name-Switcher Bot

A tiny Telegram bot that switches its **public display name** between a "real"
name and a "fake" name using **inline-button callbacks** and the Telegram Bot
API method [`setMyName`](https://core.telegram.org/bots/api#setmyname).

- **No dependencies** — pure Python 3 standard library (uses long polling).
- Reads the bot token and the two names from environment variables.

## How it works

1. The bot sends a message with three inline buttons:

   ```
   [ Set Real Name ] [ Set Fake Name ]
   [ Show current name ]
   ```

2. Tapping a button sends a **callback query** back to the bot
   (`update.callback_query`).
3. The bot acknowledges it with `answerCallbackQuery` and calls `setMyName`
   to change the bot's public name. "Show current name" calls `getMyName`.

## Setup

1. Talk to [@BotFather](https://t.me/BotFather) and create a bot, then copy the
   token.
2. Configure environment variables (copy `.env.example` to `.env` and edit):

   ```bash
   export TELEGRAM_BOT_TOKEN="123456:ABC-your-token-here"
   export REAL_NAME="My Real Bot"
   export FAKE_NAME="Totally Innocent Bot"
   ```

3. Run it:

   ```bash
   python3 bot.py
   ```

4. In Telegram, open a chat with your bot and send `/start`, then tap the
   buttons.

## Important: rate limits

Telegram **limits how often** you can change the bot name (a handful of times
per hour). If you toggle too fast, Telegram returns HTTP 429
("Too Many Requests"). The bot catches this and shows you a message like
"Rate limited by Telegram. Try again in N seconds." instead of crashing.

Also note: the name change is **global** for the bot — it is the name everyone
sees, not a per-chat nickname. The new name can take a short moment to appear in
all Telegram clients due to caching.

## Files

- `bot.py` — the bot.
- `.env.example` — sample environment configuration.
