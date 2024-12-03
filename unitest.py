import unittest
from unittest.mock import patch, MagicMock
import streamlit as st

from chatbot import get_user_input

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

if __name__ == "__main__":
    unittest.main()
