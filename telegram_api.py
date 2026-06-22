"""Thin wrapper around the Telegram Bot API using only the standard library."""

import json
import urllib.error
import urllib.parse
import urllib.request

import config


def api_request(method, params=None, timeout=60):
    """Call a Bot API method and return the parsed JSON response.

    On HTTP errors (e.g. 429 rate limit) Telegram still returns a JSON body,
    which is parsed and returned so callers can inspect error details.
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
            return json.loads(body)
        except json.JSONDecodeError:
            return {"ok": False, "error_code": exc.code, "description": body}
    except urllib.error.URLError as exc:
        return {"ok": False, "description": "Network error: {}".format(exc.reason)}


def send_message(chat_id, text, reply_markup=None):
    """Send a text message, optionally with an inline keyboard."""
    params = {"chat_id": chat_id, "text": text}
    if reply_markup is not None:
        params["reply_markup"] = json.dumps(reply_markup)
    return api_request("sendMessage", params)


def answer_callback(callback_query_id, text="", alert=False):
    """Acknowledge a callback query (stops the button's loading spinner)."""
    return api_request(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": "true" if alert else "false",
        },
    )


def get_updates(offset=None, timeout=50):
    """Long-poll for new updates."""
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    return api_request("getUpdates", params, timeout=timeout + 10)


def get_me():
    """Return info about the bot (used to validate the token)."""
    return api_request("getMe")
