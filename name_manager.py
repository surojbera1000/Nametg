"""Functions that change and read the bot's public display name.

These wrap the Telegram Bot API methods `setMyName` and `getMyName`.
"""

import config
import telegram_api


def set_name(name):
    """Set the bot's display name. Returns (ok: bool, message: str)."""
    resp = telegram_api.api_request("setMyName", {"name": name})
    if resp.get("ok"):
        return True, '✅ Name changed to "{}".'.format(name)

    desc = resp.get("description", "Unknown error")
    if resp.get("error_code") == 429:
        retry = resp.get("parameters", {}).get("retry_after")
        if retry:
            desc = "Rate limited by Telegram. Try again in {} seconds.".format(retry)
    return False, "⚠️ Could not change name: {}".format(desc)


def set_real_name():
    """Switch the bot to its configured REAL name."""
    return set_name(config.REAL_NAME)


def set_fake_name():
    """Switch the bot to its configured FAKE name."""
    return set_name(config.FAKE_NAME)


def get_current_name():
    """Return the bot's current display name, or None on failure."""
    resp = telegram_api.api_request("getMyName")
    if resp.get("ok"):
        return resp["result"].get("name", "")
    return None
