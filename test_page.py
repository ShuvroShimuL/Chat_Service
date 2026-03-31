import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mocking modules that are not available in the environment
mock_st = MagicMock()
mock_pyrebase = MagicMock()

sys.modules["streamlit"] = mock_st
sys.modules["pyrebase"] = mock_pyrebase

# We also need to mock the objects returned by pyrebase
mock_firebase = MagicMock()
mock_pyrebase.initialize_app.return_value = mock_firebase
mock_auth = MagicMock()
mock_firebase.auth.return_value = mock_auth
mock_db = MagicMock()
mock_firebase.database.return_value = mock_db

# Mocking SpeechRecognition as well since chatbot.py might be imported or needed elsewhere
sys.modules["speech_recognition"] = MagicMock()
sys.modules["groq"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.messages"] = MagicMock()
sys.modules["langchain"] = MagicMock()
sys.modules["langchain.chains"] = MagicMock()
sys.modules["langchain.chains.conversation"] = MagicMock()
sys.modules["langchain.chains.conversation.memory"] = MagicMock()
sys.modules["langchain_groq"] = MagicMock()

import page

class TestLoginPage(unittest.TestCase):
    def setUp(self):
        # Reset mocks before each test
        mock_st.reset_mock()
        mock_auth.reset_mock()
        mock_db.reset_mock()

    @patch("page.st.button")
    @patch("page.st.text_input")
    @patch("page.auth.sign_in_with_email_and_password")
    @patch("page.subprocess.Popen")
    @patch("page.os._exit")
    def test_login_success(self, mock_exit, mock_popen, mock_sign_in, mock_text_input, mock_button):
        # Simulate button click
        mock_button.return_value = True
        mock_text_input.side_effect = ["test@example.com", "password123"]

        # Call login
        page.login()

        # Verify success path
        mock_sign_in.assert_called_once_with("test@example.com", "password123")
        mock_st.success.assert_called_once_with("Logged in successfully!")
        mock_popen.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch("page.st.button")
    @patch("page.st.text_input")
    @patch("page.auth.sign_in_with_email_and_password")
    def test_login_failure(self, mock_sign_in, mock_text_input, mock_button):
        # Simulate button click
        mock_button.return_value = True
        mock_text_input.side_effect = ["test@example.com", "wrongpassword"]

        # Mock sign_in to raise an exception
        mock_sign_in.side_effect = Exception("Auth failed")

        # Call login
        page.login()

        # Verify error path
        mock_sign_in.assert_called_once_with("test@example.com", "wrongpassword")
        mock_st.warning.assert_called_once_with("Incorrect email or Incorrect password!")



class TestSignUpPage(unittest.TestCase):
    def setUp(self):
        # Reset mocks before each test
        mock_st.reset_mock()
        mock_auth.reset_mock()
        mock_db.reset_mock()

    @patch("page.st.button")
    @patch("page.st.text_input")
    def test_sign_up_invalid_email(self, mock_text_input, mock_button):
        mock_button.return_value = True
        mock_text_input.side_effect = ["invalidemail", "password123", "handle"]

        page.sign_up()

        mock_st.warning.assert_called_once_with("Please enter a valid email address")
        mock_auth.create_user_with_email_and_password.assert_not_called()

    @patch("page.st.button")
    @patch("page.st.text_input")
    def test_sign_up_short_password(self, mock_text_input, mock_button):
        mock_button.return_value = True
        mock_text_input.side_effect = ["test@example.com", "short", "handle"]

        page.sign_up()

        mock_st.warning.assert_called_once_with("Password must be at least 6 characters long")
        mock_auth.create_user_with_email_and_password.assert_not_called()

    @patch("page.st.button")
    @patch("page.st.text_input")
    def test_sign_up_empty_handle(self, mock_text_input, mock_button):
        mock_button.return_value = True
        mock_text_input.side_effect = ["test@example.com", "password123", ""]

        page.sign_up()

        mock_st.warning.assert_called_once_with("Please enter a valid user name")
        mock_auth.create_user_with_email_and_password.assert_not_called()

    @patch("page.st.button")
    @patch("page.st.text_input")
    @patch("page.auth.create_user_with_email_and_password")
    @patch("page.auth.sign_in_with_email_and_password")
    def test_sign_up_success(self, mock_sign_in, mock_create, mock_text_input, mock_button):
        mock_button.return_value = True
        mock_text_input.side_effect = ["test@example.com", "password123", "handle123"]

        # Mock user return values
        mock_create.return_value = {"localId": "12345"}
        mock_sign_in.return_value = {"localId": "12345"}

        page.sign_up()

        mock_create.assert_called_once_with("test@example.com", "password123")
        mock_sign_in.assert_called_once_with("test@example.com", "password123")

        mock_st.success.assert_called_once_with("Your account is created suceesfully!")




if __name__ == "__main__":
    unittest.main()
