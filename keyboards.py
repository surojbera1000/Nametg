"""Inline keyboards for the bot.

Telegram does not let bots set custom button background colours, so we make the
buttons "colourful" with emoji icons that render in colour on every client.
"""

import config


def main_keyboard():
    """The main menu: colourful Real / Fake / Show buttons."""
    return {
        "inline_keyboard": [
            [
                {"text": "🟢 Real Name", "callback_data": config.CB_REAL},
                {"text": "🔴 Fake Name", "callback_data": config.CB_FAKE},
            ],
            [
                {"text": "🔵 Show Current Name", "callback_data": config.CB_SHOW},
            ],
        ]
    }
