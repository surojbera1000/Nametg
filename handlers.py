"""Update handlers: react to text messages and inline-button callbacks."""

import config
import keyboards
import name_manager
import telegram_api

WELCOME_TEXT = (
    "👋 Hi! I can switch my display name.\n\n"
    "🟢 Real name: {real}\n"
    "🔴 Fake name: {fake}\n\n"
    "Pick an option below 👇"
)


def handle_message(message):
    """Handle plain text messages such as /start and /menu."""
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    if chat_id is None:
        return

    if text.startswith("/start") or text.startswith("/menu"):
        telegram_api.send_message(
            chat_id,
            WELCOME_TEXT.format(real=config.REAL_NAME, fake=config.FAKE_NAME),
            reply_markup=keyboards.main_keyboard(),
        )
    else:
        telegram_api.send_message(
            chat_id,
            "Choose an action 👇",
            reply_markup=keyboards.main_keyboard(),
        )


def handle_callback(callback):
    """Handle an inline-button tap (callback query)."""
    cb_id = callback["id"]
    data = callback.get("data", "")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")

    if data == config.CB_REAL:
        ok, msg = name_manager.set_real_name()
        telegram_api.answer_callback(cb_id, msg, alert=not ok)
    elif data == config.CB_FAKE:
        ok, msg = name_manager.set_fake_name()
        telegram_api.answer_callback(cb_id, msg, alert=not ok)
    elif data == config.CB_SHOW:
        current = name_manager.get_current_name()
        if current is None:
            telegram_api.answer_callback(
                cb_id, "⚠️ Could not fetch the current name.", alert=True
            )
        else:
            shown = current if current else "(empty — uses the bot's username)"
            telegram_api.answer_callback(
                cb_id, "🔵 Current name: {}".format(shown), alert=True
            )
    else:
        telegram_api.answer_callback(cb_id, "Unknown action.")

    if chat_id is not None:
        telegram_api.send_message(
            chat_id, "Choose an action 👇", reply_markup=keyboards.main_keyboard()
        )


def process_update(update):
    """Route an update to the right handler."""
    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_message(update["message"])
