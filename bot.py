#!/usr/bin/env python3
"""
Telegram bot that toggles its public display name between a "real" name and a
"fake" name using inline-button callbacks.

It uses ONLY the Python standard library (urllib) and the Telegram Bot API via
long polling, so there is nothing to install.

How it works
------------
- The bot sends a message with three inline buttons:
    [ Set Real Name ] [ Set Fake Name ] [ Show current name ]
- Tapping a button sends a "callback query" back to the bot.
- The bot answers the callback and calls the Bot API method `setMyName`
  to change the bot's public display name.

Setup
-----
1. Create a bot with @BotFather and copy the token.
2. Export the token (and optionally the names):
       export TELEGRAM_BOT_TOKEN="123456:ABC-..."
       export REAL_NAME="My Real Bot"
       export FAKE_NAME="Totally Innocent Bot"
3. Run it:
       python3 bot.py

Note
----
Telegram rate-limits `setMyName`. You can only change the name a limited number
of times per hour. If you toggle too quickly, Telegram returns an error
(HTTP 429 / "Too Many Requests"); this script reports that back to you instead
of crashing.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.telegram.org/bot{token}/{method}"

# ---- Configuration (via environment variables, with sensible defaults) -------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
REAL_NAME = os.environ.get("REAL_NAME", "My Real Bot Name").strip()
FAKE_NAME = os.environ.get("FAKE_NAME", "My Fake Bot Name").strip()

# Callback data identifiers sent by the inline buttons.
CB_REAL = "set_real"
CB_FAKE = "set_fake"
CB_SHOW = "show_name"


def api_request(method, params=None, timeout=60):
    """Call a Telegram Bot API method and return the parsed JSON response.

    Returns a dict. On HTTP errors (e.g. 429 rate limit) Telegram still returns
    a JSON body describing the problem, which we parse and return.
    """
    url = API_BASE.format(token=TOKEN, method=method)
    data = None
    if params is not None:
        data = urllib.parse.urlencode(params).encode("utf-8")

    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"ok": False, "error_code": exc.code, "description": body}
    except urllib.error.URLError as exc:
        return {"ok": False, "description": "Network error: {}".format(exc.reason)}


def build_keyboard():
    """The inline keyboard shown to the user."""
    return {
        "inline_keyboard": [
            [
                {"text": "Set Real Name", "callback_data": CB_REAL},
                {"text": "Set Fake Name", "callback_data": CB_FAKE},
            ],
            [
                {"text": "Show current name", "callback_data": CB_SHOW},
            ],
        ]
    }


def send_menu(chat_id, text):
    """Send a message with the inline keyboard attached."""
    return api_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(build_keyboard()),
        },
    )


def get_my_name():
    """Return the bot's current display name (or None on failure)."""
    resp = api_request("getMyName")
    if resp.get("ok"):
        return resp["result"].get("name", "")
    return None


def set_my_name(name):
    """Change the bot's display name. Returns (ok: bool, message: str)."""
    resp = api_request("setMyName", {"name": name})
    if resp.get("ok"):
        return True, 'Name changed to "{}".'.format(name)

    desc = resp.get("description", "Unknown error")
    code = resp.get("error_code")
    if code == 429:
        retry = resp.get("parameters", {}).get("retry_after")
        if retry:
            desc = "Rate limited by Telegram. Try again in {} seconds.".format(retry)
    return False, "Could not change name: {}".format(desc)


def answer_callback(callback_query_id, text="", alert=False):
    """Acknowledge a callback query so the loading spinner on the button stops."""
    api_request(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": "true" if alert else "false",
        },
    )


def handle_callback(callback):
    """Handle an inline-button tap."""
    cb_id = callback["id"]
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if data == CB_REAL:
        ok, msg = set_my_name(REAL_NAME)
        answer_callback(cb_id, msg, alert=not ok)
    elif data == CB_FAKE:
        ok, msg = set_my_name(FAKE_NAME)
        answer_callback(cb_id, msg, alert=not ok)
    elif data == CB_SHOW:
        current = get_my_name()
        if current is None:
            answer_callback(cb_id, "Could not fetch the current name.", alert=True)
        else:
            shown = current if current else "(empty — uses the bot's username)"
            answer_callback(cb_id, "Current name: {}".format(shown), alert=True)
    else:
        answer_callback(cb_id, "Unknown action.")

    if chat_id is not None:
        send_menu(chat_id, "Choose an action:")


def handle_message(message):
    """Handle plain text messages (e.g. /start)."""
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    if chat_id is None:
        return

    if text.startswith("/start") or text.startswith("/menu"):
        send_menu(
            chat_id,
            "Hi! I can switch my display name.\n\n"
            "Real name: {real}\n"
            "Fake name: {fake}\n\n"
            "Choose an action:".format(real=REAL_NAME, fake=FAKE_NAME),
        )
    else:
        send_menu(chat_id, "Choose an action:")


def process_update(update):
    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_message(update["message"])


def main():
    if not TOKEN:
        sys.exit(
            "ERROR: TELEGRAM_BOT_TOKEN is not set.\n"
            "Get a token from @BotFather and run:\n"
            '    export TELEGRAM_BOT_TOKEN="123456:ABC-..."'
        )

    # Verify the token works before entering the loop.
    me = api_request("getMe")
    if not me.get("ok"):
        sys.exit("ERROR: token check failed: {}".format(me.get("description")))
    bot_username = me["result"].get("username", "?")
    print("Bot @{} is running. Press Ctrl+C to stop.".format(bot_username))
    print('Real name: "{}"  |  Fake name: "{}"'.format(REAL_NAME, FAKE_NAME))

    offset = None
    while True:
        params = {"timeout": 50}
        if offset is not None:
            params["offset"] = offset
        resp = api_request("getUpdates", params, timeout=60)

        if not resp.get("ok"):
            print("getUpdates error: {}".format(resp.get("description")))
            time.sleep(3)
            continue

        for update in resp["result"]:
            offset = update["update_id"] + 1
            try:
                process_update(update)
            except Exception as exc:  # keep the loop alive on unexpected errors
                print("Error processing update {}: {}".format(update.get("update_id"), exc))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
