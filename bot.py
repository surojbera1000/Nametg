#!/usr/bin/env python3
"""Entry point for the Telegram name-switcher bot.

Run with:
    export TELEGRAM_BOT_TOKEN="7984346452:AAEUSUJYDv84NvvZGfzeLzPShPWdM9FnGNc"   # from @BotFather
    export REAL_NAME="My Real Bot"               # optional
    export FAKE_NAME="My Fake Bot"               # optional
    python3 bot.py

The bot shows colourful inline buttons to switch its public display name
between the configured real and fake names. Uses long polling and only the
Python standard library — no dependencies to install.

Project layout:
    config.py        - settings read from environment variables
    telegram_api.py  - thin Bot API wrapper (urllib)
    keyboards.py     - colourful inline keyboards
    name_manager.py  - functions that change/read the bot name
    handlers.py      - message and callback handlers
    bot.py           - this polling loop
"""

import sys
import time

import config
import handlers
import telegram_api


def main():
    if not config.TOKEN:
        sys.exit(
            "ERROR: TELEGRAM_BOT_TOKEN is not set.\n"
            "Get a token from @BotFather and run:\n"
            '    export TELEGRAM_BOT_TOKEN="123456:ABC-..."'
        )

    me = telegram_api.get_me()
    if not me.get("ok"):
        sys.exit("ERROR: token check failed: {}".format(me.get("description")))

    print("Bot @{} is running. Press Ctrl+C to stop.".format(me["result"].get("username", "?")))
    print('Real name: "{}"  |  Fake name: "{}"'.format(config.REAL_NAME, config.FAKE_NAME))

    offset = None
    while True:
        resp = telegram_api.get_updates(offset=offset)
        if not resp.get("ok"):
            print("getUpdates error: {}".format(resp.get("description")))
            time.sleep(3)
            continue

        for update in resp["result"]:
            offset = update["update_id"] + 1
            try:
                handlers.process_update(update)
            except Exception as exc:  # keep polling alive on unexpected errors
                print("Error processing update {}: {}".format(update.get("update_id"), exc))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
