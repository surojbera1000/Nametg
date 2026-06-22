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


def _load_dotenv():
    """Load key=value pairs from a `.env` file next to this module.

    Pure standard library — no external dependency. Values already present in
    the real environment take priority (so you can still override at runtime).
    Lines that are blank or start with '#' are ignored.
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            # Strip optional surrounding quotes from the value.
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


# Load the .env file before reading any settings.
_load_dotenv()

# Token from @BotFather (read from .env or the environment). Never hardcode it.
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

# The two names the bot toggles between.
REAL_NAME = os.environ.get("REAL_NAME", "My Real Bot Name").strip()
FAKE_NAME = os.environ.get("FAKE_NAME", "My Fake Bot Name").strip()

# Base URL template for every Bot API call.
API_BASE = "https://api.telegram.org/bot{token}/{method}"

# Callback-data identifiers used by the inline buttons.
CB_REAL = "set_real"
CB_FAKE = "set_fake"
CB_SHOW = "show_name"
