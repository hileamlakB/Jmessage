import unittest
from unittest.mock import MagicMock, patch
from ..src.gui_client import JarvesClientGUI


class TestJarvesClientGUI(unittest.TestCase):
    def setUp(self):
        addresses = ['127.0.0.1:5000']
        self.jarves_client_gui = JarvesClientGUI(addresses)
        self.jarves_client_gui.stub = MagicMock()

    def test_signup(self):
        self.jarves_client_gui.username_entry.insert(0, "testuser")
        self.jarves_client_gui.password_entry.insert(0, "testpassword")

        self.jarves_client_gui.stub.CreateAccount.return_value = MagicMock(
            error_code=0, error_message="")
        self.jarves_client_gui.signup()

        self.assertEqual(self.jarves_client_gui.user_session_id, "")

    def test_login(self):
        self.jarves_client_gui.username_entry.insert(0, "testuser")
        self.jarves_client_gui.password_entry.insert(0, "testpassword")

        self.jarves_client_gui.stub.Login.return_value = MagicMock(
            session_id="12345", error_code=0, error_message="")
        self.jarves_client_gui.login()

        self.assertEqual(self.jarves_client_gui.user_session_id, "12345")

    def test_logout(self):
        self.jarves_client_gui.user_session_id = "12345"

        self.jarves_client_gui.stub.Logout.return_value = MagicMock(
            error_code=0, error_message="")
        self.jarves_client_gui.logout()

        self.assertEqual(self.jarves_client_gui.user_session_id, "")

    def test_send_message(self):
        self.jarves_client_gui.user_session_id = "12345"
        self.jarves_client_gui.recipient_combobox.set("testrecipient")
        self.jarves_client_gui.message_entry.insert(0, "test message")

        self.jarves_client_gui.stub.SendMessage.return_value = MagicMock(
            error_code=0, error_message="")
        self.jarves_client_gui.send_message()

        self.jarves_client_gui.stub.SendMessage.assert_called_once()

    def test_clear_chat(self):
        self.jarves_client_gui.chat_text.configure(state='normal')
        self.jarves_client_gui.chat_text.insert(
            tk.END, "Sample chat content\n")
        self.jarves_client_gui.chat_text.configure(state='disabled')

        self.jarves_client_gui.clear_chat()

        content = self.jarves_client_gui.chat_text.get(1.0, tk.END)
        self.assertEqual(content, "")

    # Add additional tests for other functions here


if __name__ == '__main__':
    unittest.main()
