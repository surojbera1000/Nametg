"""Configuration for the Telegram name-switcher bot.

All sensitive / environment-specific values are read from environment
variables so nothing secret is ever committed to the repository.

Required:
    TELEGRAM_BOT_TOKEN  - token from @BotFather

Optional:
    REAL_NAME           - the "real" display name (default below)
    FAKE_NAME           - the "fake" display name (default below)
"""

import os

# Token from @BotFather. NEVER hardcode this in the file.
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
