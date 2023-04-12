import unittest
from unittest.mock import MagicMock
from src.base_client import JarvesClientBase
import spec_pb2


class TestJarvesClientBase(unittest.TestCase):
    def setUp(self):
        self.addresses = ["localhost:50051", "localhost:50052"]
        self.jarves_client = JarvesClientBase(self.addresses)
        self.jarves_client.stub = MagicMock()

    def test_create_account(self):
        username = "testuser"
        password = "testpassword"
        success_msg = "Account created successfully"

        self.jarves_client.stub.CreateAccount.return_value = MagicMock(
            error_code=0, error_message=success_msg)
        response = self.jarves_client.create_account(username, password)

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message, success_msg)
        self.jarves_client.stub.CreateAccount.assert_called_once_with(
            spec_pb2.CreateAccountRequest(username=username, password=password))

    # ... (other test methods) ...

    def test_multi_client_communication(self):
        # Create clients
        client1 = JarvesClientBase(self.addresses)
        client1.stub = MagicMock()
        client2 = JarvesClientBase(self.addresses)
        client2.stub = MagicMock()

        # Test create account
        self.jarves_client.stub.CreateAccount.side_effect = [
            MagicMock(error_code=0, error_message="Account created successfully"),
            MagicMock(error_code=0, error_message="Account created successfully")
        ]
        response1 = client1.create_account("client_1", "client_1")
        response2 = client2.create_account("client_2", "client_2")

        self.assertEqual(response1.error_code, 0)
        self.assertEqual(response1.error_message,
                         "Account created successfully")
        self.assertEqual(response2.error_code, 0)
        self.assertEqual(response2.error_message,
                         "Account created successfully")

        # Test login
        self.jarves_client.stub.Login.side_effect = [
            MagicMock(session_id="session1", error_code=0,
                      error_message="Login successful"),
            MagicMock(session_id="session2", error_code=0,
                      error_message="Login successful")
        ]
        response1 = client1.login("client_1", "client_1")
        response2 = client2.login("client_2", "client_2")

        self.assertEqual(response1.session_id, "session1")
        self.assertEqual(response1.error_code, 0)
        self.assertEqual(response1.error_message, "Login successful")
        self.assertEqual(response2.session_id, "session2")
        self.assertEqual(response2.error_code, 0)
        self.assertEqual(response2.error_message, "Login successful")

        # Test send message
        self.jarves_client.stub.Send.return_value = MagicMock(
            error_code=0, error_message="Message sent successfully")
        response = client1.send_message("client_2", "Hello client_2")

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message, "Message sent successfully")

        # Test receive message
        self.jarves_client.stub.ReceiveMessage.return_value = MagicMock(
            messages=[spec_pb2.Message(sender="client_1", content="Hello client_2", id="1")])
        response = client2.receive_messages()

        self.assertEqual(len(response.messages), 1)
        self.assertEqual(response.messages[0].sender, "client_1")
        self.assertEqual(response.messages[0].content, "Hello client_2")
        self.assertEqual(response.messages[0].id, "1")

        # Test delete account
        self.jarves_client.stub.DeleteAccount.return_value = MagicMock(
            error_code=0, error_message="Account deleted successfully")
        response = client1.delete_account()

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message,
                         "Account deleted successfully")


if __name__ == "__main__":
    unittest.main()
