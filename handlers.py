"""Update handlers: react to text messages and inline-button callbacks."""

import config
import keyboards
import name_manager
import telegram_api

MENU_TEXT = (
    "👋 I can switch my display name.\n\n"
    "🟢 Real name: {real}\n"
    "🔴 Fake name: {fake}\n\n"
    "Pick an option below 👇"
)


def _menu_text():
    return MENU_TEXT.format(real=config.REAL_NAME, fake=config.FAKE_NAME)


def handle_message(message):
    """Handle plain text messages such as /start and /menu."""
    chat_id = message.get("chat", {}).get("id")
    if chat_id is None:
        return
    telegram_api.send_message(
        chat_id, _menu_text(), reply_markup=keyboards.main_keyboard()
    )


def handle_callback(callback):
    """Handle an inline-button tap (callback query)."""
    cb_id = callback.get("id")
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if data == config.CB_REAL:
        ok, result = name_manager.set_real_name()
    elif data == config.CB_FAKE:
        ok, result = name_manager.set_fake_name()
    elif data == config.CB_SHOW:
        current = name_manager.get_current_name()
        if current is None:
            ok, result = False, "⚠️ Could not fetch the current name."
        else:
            shown = current if current else "(empty — uses the bot's username)"
            ok, result = True, "🔵 Current name: {}".format(shown)
    else:
        ok, result = False, "Unknown action."

    # Pop up the result on the button, then refresh the menu message in place.
    if cb_id is not None:
        telegram_api.answer_callback_query(cb_id, result, show_alert=not ok)

    if chat_id is not None and message_id is not None:
        telegram_api.edit_message_text(
            chat_id,
            message_id,
            "{}\n\n{}".format(_menu_text(), result),
            reply_markup=keyboards.main_keyboard(),
        )


def process_update(update):
    """Route an update to the right handler."""
    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_message(update["message"])
