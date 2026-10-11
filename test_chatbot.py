import os
import runpy
import sys
import unittest
from unittest.mock import MagicMock, patch

from test_helpers import USER, load_app


class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.chatbot = self.app.chatbot
        self.ui = self.app.st
        self.ui.session_state["user"] = USER.copy()

    def test_initial_render_does_not_submit_empty_prompt(self):
        self.ui.text_input.return_value = ""
        with patch.object(self.chatbot, "get_response") as respond:
            self.chatbot.get_user_input()
        respond.assert_not_called()

    def test_typed_question_requires_submission(self):
        self.ui.text_input.return_value = "Previous question"
        with patch.object(self.chatbot, "get_response") as respond:
            self.chatbot.get_user_input()
        respond.assert_not_called()

    def test_send_submits_trimmed_question(self):
        self.ui.text_input.return_value = "  What is AI?  "
        self.ui.form_submit_button.return_value = True
        with patch.object(self.chatbot, "get_response") as respond:
            self.chatbot.get_user_input()
        respond.assert_called_once_with("What is AI?")

    def test_empty_submission_does_not_invoke_model(self):
        self.ui.text_input.return_value = "   "
        self.ui.form_submit_button.return_value = True
        with patch.object(self.chatbot, "get_response") as respond:
            self.chatbot.get_user_input()
        respond.assert_not_called()
        self.ui.warning.assert_called_once_with("Please enter a question.")

    def test_voice_button_submits_recognized_question(self):
        self.ui.text_input.return_value = ""
        self.ui.button.side_effect = [False, True]
        with (
            patch.object(self.chatbot, "voice_interact", return_value="Voice question"),
            patch.object(self.chatbot, "get_response") as respond,
        ):
            self.chatbot.get_user_input()
        respond.assert_called_once_with("Voice question")

    def test_failed_voice_does_not_submit(self):
        self.ui.button.side_effect = [False, True]
        with (
            patch.object(self.chatbot, "voice_interact", return_value=None),
            patch.object(self.chatbot, "get_response") as respond,
        ):
            self.chatbot.get_user_input()
        respond.assert_not_called()

    def test_exit_clears_session_without_model_or_process_calls(self):
        self.ui.button.return_value = True
        self.ui.session_state.update(
            conversation=MagicMock(), chat_history=[{"human": "secret", "AI": "answer"}]
        )
        with (
            patch.object(self.chatbot, "get_response") as respond,
            patch("subprocess.Popen") as popen,
            patch("os._exit") as process_exit,
        ):
            self.chatbot.get_user_input()
        respond.assert_not_called()
        popen.assert_not_called()
        process_exit.assert_not_called()
        self.assertEqual(self.ui.session_state, {})
        self.ui.rerun.assert_called_once()
        self.ui.form.assert_not_called()

    def test_unauthenticated_entry_points_do_not_invoke_model(self):
        self.ui.session_state.clear()
        self.chatbot.main()
        self.chatbot.get_user_input()
        self.chatbot.get_response("Unauthorized question")
        self.chatbot.ChatGroq.assert_not_called()
        self.chatbot.ConversationChain.assert_not_called()
        self.ui.text_input.assert_not_called()
        self.ui.title.assert_not_called()
        self.assertNotIn("chat_history", self.ui.session_state)

    def test_standalone_chatbot_requires_login(self):
        self.ui.session_state.clear()
        with patch.dict(
            sys.modules, {**self.app.dependencies, "session_auth": self.app.session_auth}
        ):
            runpy.run_path(self.chatbot.__file__, run_name="__main__")
        self.ui.warning.assert_called_once_with(self.chatbot.LOGIN_REQUIRED)
        self.chatbot.ChatGroq.assert_not_called()

    def test_previous_history_is_displayed_without_resubmission(self):
        self.ui.session_state["chat_history"] = [{"human": "Hello", "AI": "Hi"}]
        with patch.object(self.chatbot, "get_response") as respond:
            self.chatbot.get_user_input()
        respond.assert_not_called()
        self.ui.write.assert_any_call("You: Hello")
        self.ui.write.assert_any_call("Chatbot 🤖: Hi")

    def test_logout_does_not_clear_another_browser_session(self):
        other = load_app()
        other.st.session_state.update(
            user=USER.copy(), chat_history=[{"human": "Other user", "AI": "Answer"}]
        )
        self.chatbot.exit_from_chatbot()
        self.assertTrue(other.session_auth.is_authenticated())
        self.assertEqual(len(other.st.session_state["chat_history"]), 1)


class TestGetResponse(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.chatbot = self.app.chatbot
        self.ui = self.app.st
        self.ui.session_state["user"] = USER.copy()
        self.chain = self.chatbot.ConversationChain.return_value
        self.chain.predict.return_value = "Mocked AI response"
        self.environment = patch.dict(
            os.environ, {"GROQ_API_KEY": "test-key"}, clear=True
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_success_uses_supported_default_and_saves_history(self):
        self.chatbot.get_response("Hi bot")
        self.chatbot.ChatGroq.assert_called_once_with(
            groq_api_key="test-key", model_name="openai/gpt-oss-120b"
        )
        self.chain.predict.assert_called_once_with(input="Hi bot")
        self.assertEqual(
            self.ui.session_state["chat_history"],
            [{"human": "Hi bot", "AI": "Mocked AI response"}],
        )

    def test_model_can_be_configured(self):
        with patch.dict(os.environ, {"GROQ_MODEL": "account-model"}):
            self.chatbot.get_response("Question")
        self.assertEqual(
            self.chatbot.ChatGroq.call_args.kwargs["model_name"], "account-model"
        )

    def test_conversation_is_reused_between_questions(self):
        self.chatbot.get_response("First")
        self.chatbot.get_response("Second")
        self.chatbot.ChatGroq.assert_called_once()
        self.chatbot.ConversationChain.assert_called_once()
        self.assertEqual(self.chain.predict.call_count, 2)
        self.assertEqual(len(self.ui.session_state["chat_history"]), 2)

    def test_new_login_gets_fresh_memory(self):
        memories = [MagicMock(), MagicMock()]
        self.chatbot.ConversationBufferWindowMemory.side_effect = memories
        self.chatbot.get_response("First user's question")
        self.app.session_auth.start_session(
            {"localId": "user456", "idToken": "other-token"}
        )
        self.chatbot.get_response("Second user's question")
        self.assertEqual(self.chatbot.ConversationChain.call_count, 2)
        self.assertIs(
            self.chatbot.ConversationChain.call_args_list[0].kwargs["memory"], memories[0]
        )
        self.assertIs(
            self.chatbot.ConversationChain.call_args_list[1].kwargs["memory"], memories[1]
        )
        self.assertEqual(len(self.ui.session_state["chat_history"]), 1)

    def test_blank_or_missing_question_never_calls_model(self):
        for question in ("", "   ", None):
            self.chatbot.get_response(question)
        self.chatbot.ChatGroq.assert_not_called()
        self.chain.predict.assert_not_called()

    def test_missing_key_does_not_initialize_conversation(self):
        with patch.dict(os.environ, {}, clear=True):
            self.chatbot.get_response("Question")
        self.chatbot.ChatGroq.assert_not_called()
        self.assertNotIn("conversation", self.ui.session_state)
        self.ui.error.assert_called_once()

    def test_client_initialization_failure_is_handled(self):
        self.chatbot.ChatGroq.side_effect = RuntimeError("Invalid configuration")
        self.chatbot.get_response("Question")
        self.ui.warning.assert_called_once()
        self.assertNotIn("conversation", self.ui.session_state)
        self.assertEqual(self.ui.session_state["chat_history"], [])

    def test_prediction_failure_does_not_append_history(self):
        self.chain.predict.side_effect = RuntimeError("API error")
        self.chatbot.get_response("Question")
        self.ui.warning.assert_called_once()
        self.assertEqual(self.ui.session_state["chat_history"], [])


class TestVoiceInteract(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.chatbot = self.app.chatbot

    def test_voice_interact_success(self):
        recognizer = self.chatbot.sr.Recognizer.return_value
        recognizer.recognize_google.return_value = "Hello world"
        result = self.chatbot.voice_interact()
        source = self.chatbot.sr.Microphone.return_value.__enter__.return_value
        recognizer.listen.assert_called_once_with(source, timeout=20)
        recognizer.recognize_google.assert_called_once_with(
            recognizer.listen.return_value
        )
        self.app.st.text.assert_called_once_with("🗣 : Hello world")
        self.assertEqual(result, "Hello world")

    def test_voice_interact_failure(self):
        self.chatbot.sr.Recognizer.return_value.listen.side_effect = RuntimeError(
            "Microphone error"
        )
        self.assertIsNone(self.chatbot.voice_interact())
        self.app.st.warning.assert_called_once_with("Failed to understand!")


if __name__ == "__main__":
    unittest.main()
