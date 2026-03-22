import unittest
from unittest.mock import patch, MagicMock
import sys

# Mocking modules that are not available in the environment
sys.modules["streamlit"] = MagicMock()
sys.modules["pyrebase"] = MagicMock()
sys.modules["speech_recognition"] = MagicMock()
sys.modules["groq"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.messages"] = MagicMock()
sys.modules["langchain"] = MagicMock()
sys.modules["langchain.chains"] = MagicMock()
sys.modules["langchain.chains.conversation"] = MagicMock()
sys.modules["langchain.chains.conversation.memory"] = MagicMock()
sys.modules["langchain_groq"] = MagicMock()

import streamlit as st
from chatbot import get_user_input, get_response

class SessionStateMock(dict):
    def __getattr__(self, item):
        return self.get(item)
    def __setattr__(self, key, value):
        self[key] = value

class TestGetUserInput(unittest.TestCase):
    @patch("chatbot.st.text_input")
    @patch("chatbot.st.button")
    @patch("chatbot.voice_interact")
    @patch("chatbot.get_response")
    def test_text_input_trigger(self, mock_get_response, mock_voice_interact, mock_button, mock_text_input):
        # Simulate user typing a question in the text input
        mock_text_input.return_value = "What is AI?"
        mock_button.return_value = False  # Button is not pressed

        get_user_input()

        # Ensure `get_response` is called with the typed question
        mock_get_response.assert_called_once_with("What is AI?")
        mock_voice_interact.assert_not_called()

    @patch("chatbot.st.text_input")
    @patch("chatbot.st.button")
    @patch("chatbot.voice_interact")
    @patch("chatbot.get_response")
    def test_voice_button_trigger(self, mock_get_response, mock_voice_interact, mock_button, mock_text_input):
        # Simulate pressing the voice button
        mock_text_input.return_value = ""
        mock_button.return_value = True  # Button is pressed
        mock_voice_interact.return_value = "Tell me about Python."

        get_user_input()

        # Ensure `get_response` is called with the voice input
        mock_get_response.assert_called_once_with("Tell me about Python.")
        mock_voice_interact.assert_called_once()


class TestGetResponse(unittest.TestCase):
    @patch("chatbot.st")
    @patch("chatbot.ChatGroq")
    @patch("chatbot.ConversationChain")
    @patch("chatbot.memory")
    def test_get_response_success(self, mock_memory, mock_conversation_chain, mock_chat_groq, mock_st):
        # Setup st.session_state as a SessionStateMock
        mock_st.session_state = SessionStateMock()

        # Configure ConversationChain instance
        mock_conversation_instance = MagicMock()
        mock_conversation_chain.return_value = mock_conversation_instance
        mock_conversation_instance.predict.return_value = "Mocked AI response"

        # Prevent exit button from being triggered
        mock_st.button.return_value = False

        # Call the function
        get_response("Hi bot")

        # Assertions for LangChain/Groq interactions
        mock_conversation_chain.assert_called_once()
        mock_conversation_instance.predict.assert_called_once_with(input="Hi bot")

        # Assertions for Streamlit output
        mock_st.write.assert_called_once_with("Chatbot 🤖: Mocked AI response")
        mock_st.success.assert_called_once_with("Response genereated successfully!")

        # Verify chat history is updated
        self.assertEqual(len(mock_st.session_state.chat_history), 1)
        self.assertEqual(
            mock_st.session_state.chat_history[0],
            {"human": "Hi bot", "AI": "Mocked AI response"}
        )

if __name__ == "__main__":
    unittest.main()
