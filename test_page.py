import unittest
from unittest.mock import patch

from test_helpers import USER, load_app


class TestLoginPage(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.page = self.app.page
        self.ui = self.app.st
        self.ui.button.return_value = True
        self.ui.text_input.side_effect = ["test@example.com", "password123"]

    def test_login_persists_user_and_reruns_without_process_calls(self):
        self.page.auth.sign_in_with_email_and_password.return_value = USER.copy()
        self.ui.session_state.update(
            conversation="old conversation", chat_history=["old history"]
        )
        with patch("subprocess.Popen") as popen, patch("os._exit") as process_exit:
            self.page.login()
        self.page.auth.sign_in_with_email_and_password.assert_called_once_with(
            "test@example.com", "password123"
        )
        self.assertEqual(self.ui.session_state, {"user": USER})
        self.ui.rerun.assert_called_once()
        popen.assert_not_called()
        process_exit.assert_not_called()

    def test_login_failure_does_not_authenticate_or_navigate(self):
        self.page.auth.sign_in_with_email_and_password.side_effect = RuntimeError(
            "Auth failed"
        )
        self.page.login()
        self.ui.warning.assert_called_once_with("Incorrect email or Incorrect password!")
        self.ui.rerun.assert_not_called()
        self.assertFalse(self.app.session_auth.is_authenticated())

    def test_incomplete_authentication_response_is_rejected(self):
        self.page.auth.sign_in_with_email_and_password.return_value = {"localId": "user123"}
        self.page.login()
        self.assertFalse(self.app.session_auth.is_authenticated())
        self.ui.rerun.assert_not_called()

    def test_authenticated_main_renders_chat_in_same_app(self):
        self.ui.session_state["user"] = USER.copy()
        with patch.object(self.page, "chat_main") as chat_main:
            self.page.main()
        chat_main.assert_called_once()
        self.ui.selectbox.assert_not_called()

    def test_unauthenticated_main_renders_login(self):
        self.ui.selectbox.return_value = "Login"
        with (
            patch.object(self.page, "login") as login,
            patch.object(self.page, "chat_main") as chat_main,
        ):
            self.page.main()
        login.assert_called_once()
        chat_main.assert_not_called()

    def test_unauthenticated_main_renders_signup(self):
        self.ui.selectbox.return_value = "Sign up"
        with (
            patch.object(self.page, "sign_up") as signup,
            patch.object(self.page, "chat_main") as chat_main,
        ):
            self.page.main()
        signup.assert_called_once()
        chat_main.assert_not_called()


class TestSignUpPage(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.page = self.app.page
        self.ui = self.app.st
        self.ui.button.return_value = True
        self.ui.text_input.side_effect = ["test@example.com", "password123", "testuser"]
        self.page.auth.create_user_with_email_and_password.return_value = USER.copy()

    def test_signup_saves_profile_with_new_users_token(self):
        self.page.sign_up()
        self.page.auth.create_user_with_email_and_password.assert_called_once_with(
            "test@example.com", "password123"
        )
        self.page.db.child.assert_called_once_with("user123")
        self.page.db.child.return_value.set.assert_called_once_with(
            {"Handle": "testuser", "Email": "test@example.com", "ID": "user123"},
            "test-token",
        )
        self.page.auth.sign_in_with_email_and_password.assert_not_called()
        self.ui.success.assert_called_once_with("Your account is created successfully!")
        self.ui.info.assert_called_once()
        self.assertFalse(self.app.session_auth.is_authenticated())

    def test_creation_failure_does_not_write_profile(self):
        self.page.auth.create_user_with_email_and_password.side_effect = RuntimeError(
            "Email exists"
        )
        self.page.sign_up()
        self.page.db.child.assert_not_called()
        self.ui.success.assert_not_called()
        self.ui.warning.assert_called_once_with(
            "Could not create your account. Check the email and password, "
            "or try logging in if you already have an account."
        )

    def test_profile_failure_does_not_report_duplicate_account(self):
        self.page.db.child.return_value.set.side_effect = PermissionError(
            "Permission denied"
        )
        self.page.sign_up()
        self.page.auth.create_user_with_email_and_password.assert_called_once()
        self.ui.success.assert_not_called()
        self.ui.balloons.assert_not_called()
        self.ui.warning.assert_called_once_with(
            "Your account was created, but your profile could not be saved. "
            "You can still log in."
        )

    def test_invalid_signup_input_never_creates_account(self):
        cases = (
            (["invalidemail", "password123", "handle"], "Please enter a valid email address"),
            (["test@example.com", "short", "handle"], "Password must be at least 6 characters long"),
            (["test@example.com", "password123", ""], "Please enter a valid user name"),
            (["test@example.com", "password123", "   "], "Please enter a valid user name"),
        )
        for inputs, warning in cases:
            with self.subTest(inputs=inputs):
                app = load_app()
                app.st.button.return_value = True
                app.st.text_input.side_effect = inputs
                app.page.sign_up()
                app.st.warning.assert_called_once_with(warning)
                app.page.auth.create_user_with_email_and_password.assert_not_called()


class TestSessionAuthentication(unittest.TestCase):
    def test_invalid_user_records_cannot_authenticate(self):
        app = load_app()
        for user in (
            None, True, {}, {"localId": "user123"},
            {"localId": "", "idToken": "token"},
            {"localId": "user123", "idToken": ""},
        ):
            with self.subTest(user=user):
                app.st.session_state["user"] = user
                self.assertFalse(app.session_auth.is_authenticated())


if __name__ == "__main__":
    unittest.main()
