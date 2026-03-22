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
from chatbot import get_user_input, voice_interact

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

class TestVoiceInteract(unittest.TestCase):
    @patch("chatbot.sr.Recognizer")
    @patch("chatbot.sr.Microphone")
    @patch("chatbot.st.text")
    def test_voice_interact_success(self, mock_st_text, mock_microphone, mock_recognizer):
        # Setup mock Recognizer
        mock_r_instance = MagicMock()
        mock_recognizer.return_value = mock_r_instance

        # Setup mock Microphone context manager
        mock_mic_instance = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_mic_instance

        # Setup audio and recognized text
        mock_audio = MagicMock()
        mock_r_instance.listen.return_value = mock_audio
        mock_r_instance.recognize_google.return_value = "Hello world"

        # Call the function
        result = voice_interact()

        # Assertions
        mock_r_instance.listen.assert_called_once_with(mock_mic_instance, timeout=20)
        mock_r_instance.recognize_google.assert_called_once_with(mock_audio)
        mock_st_text.assert_called_once_with("🗣 : Hello world")
        self.assertEqual(result, "Hello world")

    @patch("chatbot.sr.Recognizer")
    @patch("chatbot.sr.Microphone")
    @patch("chatbot.st.warning")
    def test_voice_interact_exception(self, mock_st_warning, mock_microphone, mock_recognizer):
        # Setup mock Recognizer to raise an exception
        mock_r_instance = MagicMock()
        mock_recognizer.return_value = mock_r_instance

        # Setup mock Microphone context manager
        mock_mic_instance = MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_mic_instance

        # Make listen raise an exception
        mock_r_instance.listen.side_effect = Exception("Microphone error")

        # Call the function
        result = voice_interact()

        # Assertions
        mock_st_warning.assert_called_once_with("Failed to understand!")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
