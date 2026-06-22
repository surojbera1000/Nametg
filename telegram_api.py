"""Thin wrapper around the Telegram Bot API using only the standard library."""

import json
import urllib.error
import urllib.parse
import urllib.request

import config


def request(method, params=None, timeout=60):
    """Call a Bot API method and return the parsed JSON response (a dict).

    On HTTP errors (e.g. 429 rate limit, 409 conflict) Telegram still returns a
    JSON body, which is parsed and returned so callers can inspect the error.
    Network failures return {"ok": False, "description": "..."} instead of
    raising, so the polling loop never crashes.
    """
    url = config.API_BASE.format(token=config.TOKEN, method=method)
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
            parsed = json.loads(body)
            if "ok" not in parsed:
                parsed["ok"] = False
            return parsed
        except json.JSONDecodeError:
            return {"ok": False, "error_code": exc.code, "description": body}
    except urllib.error.URLError as exc:
        return {"ok": False, "description": "Network error: {}".format(exc.reason)}
    except Exception as exc:  # pragma: no cover - defensive catch-all
        return {"ok": False, "description": "Unexpected error: {}".format(exc)}


# --- Convenience helpers -----------------------------------------------------

def get_me():
    """Return info about the bot (used to validate the token)."""
    return request("getMe")


def delete_webhook(drop_pending_updates=False):
    """Remove any configured webhook so getUpdates (long polling) can work.

    A leftover webhook is the most common reason a polling bot "doesn't
    respond" (Telegram returns 409 Conflict to getUpdates).
    """
    return request(
        "deleteWebhook",
        {"drop_pending_updates": "true" if drop_pending_updates else "false"},
    )


def get_updates(offset=None, timeout=50):
    """Long-poll for new updates."""
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    # HTTP read timeout must be a bit longer than the long-poll timeout.
    return request("getUpdates", params, timeout=timeout + 15)


def send_message(chat_id, text, reply_markup=None):
    """Send a text message, optionally with an inline keyboard."""
    params = {"chat_id": chat_id, "text": text}
    if reply_markup is not None:
        params["reply_markup"] = json.dumps(reply_markup)
    return request("sendMessage", params)


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    """Edit an existing message's text (and optionally its keyboard)."""
    params = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup is not None:
        params["reply_markup"] = json.dumps(reply_markup)
    return request("editMessageText", params)


def answer_callback_query(callback_query_id, text="", show_alert=False):
    """Acknowledge a callback query (stops the button's loading spinner)."""
    return request(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": "true" if show_alert else "false",
        },
    )


def set_my_name(name):
    """Set the bot's public display name."""
    return request("setMyName", {"name": name})


def get_my_name():
    """Get the bot's current public display name."""
    return request("getMyName")
