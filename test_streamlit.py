"""Exercise real Streamlit reruns with Firebase and Groq requests mocked."""

import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from test_helpers import USER


DEPENDENCIES_AVAILABLE = all(
    importlib.util.find_spec(name) is not None
    for name in ("streamlit", "pyrebase", "langchain_groq", "speech_recognition", "groq")
)


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "Install requirements.txt for Streamlit tests")
class TestStreamlitFlow(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest

        self.AppTest = AppTest
        self.root = Path(__file__).parent
        self.firebase = MagicMock()
        self.firebase.auth.return_value.sign_in_with_email_and_password.return_value = USER.copy()
        self.firebase.auth.return_value.create_user_with_email_and_password.return_value = USER.copy()
        firebase_patch = patch("pyrebase.initialize_app", return_value=self.firebase)
        firebase_patch.start()
        self.addCleanup(firebase_patch.stop)

        environment = patch.dict(
            os.environ,
            {
                "FIREBASE_API_KEY": "test-key",
                "GROQ_API_KEY": "test-key",
                "GROQ_MODEL": "",
                "LANGCHAIN_TRACING_V2": "false",
                "LANGCHAIN_TRACING": "false",
                "LANGSMITH_TRACING": "false",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        groq_patch = patch(
            "groq.resources.chat.completions.Completions.create",
            return_value={
                "choices": [{
                    "message": {"role": "assistant", "content": "Mocked answer"},
                    "finish_reason": "stop",
                }],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                "model": "openai/gpt-oss-120b",
            },
        )
        self.groq_request = groq_patch.start()
        self.addCleanup(groq_patch.stop)

    def app(self, file="page.py"):
        app = self.AppTest.from_file(str(self.root / file), default_timeout=10).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def click(self, app, label):
        next(button for button in app.button if button.label == label).click().run()
        self.assertEqual(len(app.exception), 0)

    def test_login_send_rerun_and_logout_in_one_app(self):
        app = self.app()
        app.text_input[0].set_value("test@example.com")
        app.text_input[1].set_value("password123")
        self.click(app, "Login")
        self.assertEqual(app.session_state["user"], USER)
        self.assertEqual(app.text_input[0].label, "Ask a question:")
        self.groq_request.assert_not_called()

        app.text_input[0].set_value("Hello")
        self.click(app, "Send")
        self.groq_request.assert_called_once()
        self.assertEqual(self.groq_request.call_args.kwargs["model"], "openai/gpt-oss-120b")
        self.assertEqual(app.session_state["chat_history"], [{"human": "Hello", "AI": "Mocked answer"}])
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.groq_request.assert_called_once()

        other = self.app()
        self.assertEqual(other.text_input[0].label, "Email Address")
        other.session_state["user"] = {"localId": "other-user", "idToken": "other-token"}
        other.run()
        self.assertEqual(len(other.exception), 0)

        self.click(app, "Exit")
        self.groq_request.assert_called_once()
        self.assertNotIn("user", app.session_state)
        self.assertNotIn("conversation", app.session_state)
        self.assertNotIn("chat_history", app.session_state)
        self.assertEqual(app.text_input[0].label, "Email Address")
        self.assertEqual(other.session_state["user"]["localId"], "other-user")

    def test_standalone_chatbot_rejects_unauthenticated_session(self):
        app = self.app("chatbot.py")
        self.assertEqual(len(app.text_input), 0)
        self.assertEqual(len(app.warning), 1)
        self.groq_request.assert_not_called()

    def test_signup_uses_authenticated_profile_write(self):
        app = self.app()
        app.selectbox[0].select("Sign up").run()
        app.text_input[0].set_value("test@example.com")
        app.text_input[1].set_value("password123")
        app.text_input[2].set_value("handle")
        self.click(app, "Create my account")
        self.firebase.database.return_value.child.return_value.set.assert_called_once_with(
            {"Handle": "handle", "Email": "test@example.com", "ID": "user123"},
            "test-token",
        )
        self.assertEqual(len(app.success), 1)


if __name__ == "__main__":
    unittest.main()
