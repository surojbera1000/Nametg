"""Configuration for the Telegram name-switcher bot.

You only need ONE place for your secret: a file named ".env" in this same
folder. Nothing needs to be exported in the shell. When the bot starts it
automatically loads ".env" from here.

.env example (copy from .env.example):
    TELEGRAM_BOT_TOKEN=123456:ABC-your-token-here
    REAL_NAME=My Real Bot Name
    FAKE_NAME=My Fake Bot Name
"""

import os


def load_dotenv(path=None):
    """Load key=value pairs from a `.env` file into os.environ.

    Pure standard library — no external dependency. Values already present in
    the real environment take priority. Blank lines and '#' comments are
    ignored. Returns a dict of the values that were loaded.
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    loaded = {}
    if not os.path.isfile(path):
        return loaded

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            # Strip optional surrounding quotes from the value.
            value = value.strip().strip('"').strip("'")
            if not key:
                continue
            loaded[key] = value
            if key not in os.environ:
                os.environ[key] = value
    return loaded


def reload():
    """(Re)read settings from the environment. Returns nothing; sets globals."""
    global TOKEN, REAL_NAME, FAKE_NAME
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    REAL_NAME = os.environ.get("REAL_NAME", "My Real Bot Name").strip()
    FAKE_NAME = os.environ.get("FAKE_NAME", "My Fake Bot Name").strip()


# Load the .env file, then read settings from the environment.
load_dotenv()
reload()

# Base URL template for every Bot API call.
API_BASE = "https://api.telegram.org/bot{token}/{method}"

# Callback-data identifiers used by the inline buttons.
CB_REAL = "set_real"
CB_FAKE = "set_fake"
CB_SHOW = "show_name"
