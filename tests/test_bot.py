"""Automated tests for the Telegram name-switcher bot.

These tests mock the Telegram API at the network boundary (telegram_api.request)
so the bot's real logic is exercised end-to-end without needing internet access.

Run from the project root:
    python3 -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest
from unittest import mock

# Make the project modules importable when tests run from any directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config  # noqa: E402
import handlers  # noqa: E402
import keyboards  # noqa: E402
import name_manager  # noqa: E402
import telegram_api  # noqa: E402


class FakeAPI:
    """Records every call to telegram_api.request and returns canned responses.

    Set `responses[method]` to control what a given method returns; otherwise a
    generic {"ok": True} is returned.
    """

    def __init__(self):
        self.calls = []          # list of (method, params) tuples
        self.responses = {}      # method name -> response dict

    def __call__(self, method, params=None, timeout=60):
        self.calls.append((method, params or {}))
        return self.responses.get(method, {"ok": True, "result": {}})

    def methods_called(self):
        return [m for m, _ in self.calls]

    def params_for(self, method):
        for m, p in self.calls:
            if m == method:
                return p
        return None


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        # Preserve real config values and env between tests.
        self._saved = (config.TOKEN, config.REAL_NAME, config.FAKE_NAME)

    def tearDown(self):
        config.TOKEN, config.REAL_NAME, config.FAKE_NAME = self._saved

    def test_dotenv_loading_parses_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = os.path.join(tmp, ".env")
            with open(env_path, "w", encoding="utf-8") as fh:
                fh.write("# a comment\n")
                fh.write('TELEGRAM_BOT_TOKEN="abc123"\n')
                fh.write("REAL_NAME=Real One\n")
                fh.write("FAKE_NAME = 'Fake Two' \n")
                fh.write("\n")  # blank line ignored

            # Ensure these keys are not already in the environment.
            for key in ("TELEGRAM_BOT_TOKEN", "REAL_NAME", "FAKE_NAME"):
                os.environ.pop(key, None)

            loaded = config.load_dotenv(env_path)
            self.assertEqual(loaded["TELEGRAM_BOT_TOKEN"], "abc123")
            self.assertEqual(loaded["REAL_NAME"], "Real One")
            self.assertEqual(loaded["FAKE_NAME"], "Fake Two")

            config.reload()
            self.assertEqual(config.TOKEN, "abc123")
            self.assertEqual(config.REAL_NAME, "Real One")
            self.assertEqual(config.FAKE_NAME, "Fake Two")

            # Cleanup env we set.
            for key in ("TELEGRAM_BOT_TOKEN", "REAL_NAME", "FAKE_NAME"):
                os.environ.pop(key, None)

    def test_token_is_read_from_correct_env_var(self):
        # Regression test for the bug where TOKEN looked up the wrong key.
        os.environ["TELEGRAM_BOT_TOKEN"] = "tok-xyz"
        try:
            config.reload()
            self.assertEqual(config.TOKEN, "tok-xyz")
        finally:
            os.environ.pop("TELEGRAM_BOT_TOKEN", None)


class KeyboardTestCase(unittest.TestCase):
    def test_main_keyboard_structure(self):
        kb = keyboards.main_keyboard()
        rows = kb["inline_keyboard"]
        # Flatten all buttons.
        buttons = [btn for row in rows for btn in row]
        callbacks = {btn["callback_data"] for btn in buttons}
        self.assertEqual(
            callbacks, {config.CB_REAL, config.CB_FAKE, config.CB_SHOW}
        )
        # Buttons should be colourful (contain an emoji icon).
        for btn in buttons:
            self.assertTrue(any(ord(ch) > 0x2000 for ch in btn["text"]),
                            "button '{}' has no emoji".format(btn["text"]))


class NameManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()
        self.patcher = mock.patch.object(telegram_api, "request", self.api)
        self.patcher.start()
        self._saved = (config.REAL_NAME, config.FAKE_NAME)
        config.REAL_NAME = "Real Bot"
        config.FAKE_NAME = "Fake Bot"

    def tearDown(self):
        self.patcher.stop()
        config.REAL_NAME, config.FAKE_NAME = self._saved

    def test_set_real_name_calls_setmyname_with_real(self):
        ok, msg = name_manager.set_real_name()
        self.assertTrue(ok)
        self.assertEqual(self.api.params_for("setMyName"), {"name": "Real Bot"})
        self.assertIn("Real Bot", msg)

    def test_set_fake_name_calls_setmyname_with_fake(self):
        ok, msg = name_manager.set_fake_name()
        self.assertTrue(ok)
        self.assertEqual(self.api.params_for("setMyName"), {"name": "Fake Bot"})

    def test_rate_limit_is_reported_friendly(self):
        self.api.responses["setMyName"] = {
            "ok": False,
            "error_code": 429,
            "description": "Too Many Requests",
            "parameters": {"retry_after": 42},
        }
        ok, msg = name_manager.set_real_name()
        self.assertFalse(ok)
        self.assertIn("42 seconds", msg)

    def test_get_current_name_returns_value(self):
        self.api.responses["getMyName"] = {"ok": True, "result": {"name": "Hello"}}
        self.assertEqual(name_manager.get_current_name(), "Hello")

    def test_get_current_name_returns_none_on_failure(self):
        self.api.responses["getMyName"] = {"ok": False, "description": "nope"}
        self.assertIsNone(name_manager.get_current_name())


class HandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()
        self.patcher = mock.patch.object(telegram_api, "request", self.api)
        self.patcher.start()
        self._saved = (config.REAL_NAME, config.FAKE_NAME)
        config.REAL_NAME = "Real Bot"
        config.FAKE_NAME = "Fake Bot"

    def tearDown(self):
        self.patcher.stop()
        config.REAL_NAME, config.FAKE_NAME = self._saved

    def _callback_update(self, data):
        return {
            "callback_query": {
                "id": "cb1",
                "data": data,
                "message": {"message_id": 99, "chat": {"id": 555}},
            }
        }

    def test_start_message_sends_menu_with_keyboard(self):
        update = {"message": {"chat": {"id": 555}, "text": "/start"}}
        handlers.process_update(update)
        self.assertIn("sendMessage", self.api.methods_called())
        params = self.api.params_for("sendMessage")
        self.assertEqual(params["chat_id"], 555)
        self.assertIn("reply_markup", params)

    def test_callback_real_sets_name_and_answers(self):
        handlers.process_update(self._callback_update(config.CB_REAL))
        called = self.api.methods_called()
        self.assertIn("setMyName", called)
        self.assertIn("answerCallbackQuery", called)
        self.assertIn("editMessageText", called)
        self.assertEqual(self.api.params_for("setMyName"), {"name": "Real Bot"})

    def test_callback_fake_sets_fake_name(self):
        handlers.process_update(self._callback_update(config.CB_FAKE))
        self.assertEqual(self.api.params_for("setMyName"), {"name": "Fake Bot"})

    def test_callback_show_uses_getmyname(self):
        self.api.responses["getMyName"] = {"ok": True, "result": {"name": "Now"}}
        handlers.process_update(self._callback_update(config.CB_SHOW))
        self.assertIn("getMyName", self.api.methods_called())
        # Should NOT change the name when just showing it.
        self.assertNotIn("setMyName", self.api.methods_called())

    def test_callback_answers_with_alert_on_failure(self):
        self.api.responses["setMyName"] = {
            "ok": False, "error_code": 400, "description": "bad"
        }
        handlers.process_update(self._callback_update(config.CB_REAL))
        answer = self.api.params_for("answerCallbackQuery")
        self.assertEqual(answer["show_alert"], "true")


class ApiErrorHandlingTestCase(unittest.TestCase):
    """Verify the low-level request() never raises on network failure."""

    def test_network_error_returns_dict_not_raises(self):
        import urllib.error

        def boom(req, timeout=60):
            raise urllib.error.URLError("no network")

        with mock.patch("urllib.request.urlopen", side_effect=boom):
            resp = telegram_api.request("getMe")
        self.assertFalse(resp["ok"])
        self.assertIn("Network error", resp["description"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
