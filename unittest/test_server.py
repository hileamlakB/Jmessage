import unittest
from ..src.server import ClientService, User  # Replace with your server file name
from ..src import spec_pb2
from ..src import spec_pb2_grpc

class TestClientService(unittest.TestCase):

    def setUp(self):
        self.client_service = ClientService()

    def test_create_account(self):
        request = spec_pb2.CreateAccountRequest(username="test_user", password="test_password")
        response = self.client_service.CreateAccount(request, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.SUCCESS)
        self.assertEqual(response.error_message, "Account created successfully!!")

    def test_create_account_existing_user(self):
        request = spec_pb2.CreateAccountRequest(username="test_user", password="test_password")
        self.client_service.CreateAccount(request, None)  # Creating the account first

        response = self.client_service.CreateAccount(request, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.USER_NAME_EXISTS)
        self.assertEqual(response.error_message, "Username already exists!!")

    def test_login_success(self):
        request_create_account = spec_pb2.CreateAccountRequest(username="test_user", password="test_password")
        self.client_service.CreateAccount(request_create_account, None)

        request_login = spec_pb2.LoginRequest(username="test_user", password="test_password")
        response = self.client_service.Login(request_login, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.SUCCESS)
        self.assertEqual(response.error_message, "Login successful!!")
        self.assertIsNotNone(response.session_id)

    def test_login_non_existent_user(self):
        request_login = spec_pb2.LoginRequest(username="non_existent_user", password="test_password")
        response = self.client_service.Login(request_login, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.USER_DOESNT_EXIST)
        self.assertEqual(response.error_message, "User doesn't exist!!")

    def test_login_wrong_password(self):
        request_create_account = spec_pb2.CreateAccountRequest(username="test_user", password="test_password")
        self.client_service.CreateAccount(request_create_account, None)

        request_login = spec_pb2.LoginRequest(username="test_user", password="wrong_password")
        response = self.client_service.Login(request_login, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.INCORRECT_PASSWORD)
        self.assertEqual(response.error_message, "Incorrect password!!")

    def test_send_message(self):
        # Create sender and receiver accounts and log them in
        sender_username = "sender"
        receiver_username = "receiver"
        password = "password"
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=sender_username, password=password), None)
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=receiver_username, password=password), None)
        sender_session_id = self.client_service.Login(spec_pb2.LoginRequest(username=sender_username, password=password), None).session_id
        receiver_session_id = self.client_service.Login(spec_pb2.LoginRequest(username=receiver_username, password=password), None).session_id

        # Send a message
        request = spec_pb2.SendMessageRequest(session_id=sender_session_id, to=receiver_username, message="Test message")
        response = self.client_service.Send(request, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.SUCCESS)
        self.assertEqual(response.error_message, "Message sent successfully!!")

    def test_list_users(self):
        # Create accounts and log them in
        username1 = "user1"
        username2 = "user2"
        password = "password"
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=username1, password=password), None)
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=username2, password=password), None)
        self.client_service.Login(spec_pb2.LoginRequest(username=username1, password=password), None)
        self.client_service.Login(spec_pb2.LoginRequest(username=username2, password=password), None)

        request = spec_pb2.ListUsersRequest()
        response = self.client_service.ListUsers(request, None)

        self.assertEqual(len(response.user), 2)
        self.assertIn(username1, [user.username for user in response.user])
        self.assertIn(username2, [user.username for user in response.user])

    def test_receive_message(self):
        # Create sender and receiver accounts, log them in, and send a message
        sender_username = "sender"
        receiver_username = "receiver"
        password = "password"
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=sender_username, password=password), None)
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=receiver_username, password=password), None)
        sender_session_id = self.client_service.Login(spec_pb2.LoginRequest(username=sender_username, password=password), None).session_id
        receiver_session_id = self.client_service.Login(spec_pb2.LoginRequest(username=receiver_username, password=password), None).session_id
        message_content = "Test message"
        self.client_service.Send(spec_pb2.SendMessageRequest(session_id=sender_session_id, to=receiver_username, message=message_content), None)

        # Receive the message
        request = spec_pb2.ReceiveMessageRequest(session_id=receiver_session_id)
        response = self.client_service.ReceiveMessage(request, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.SUCCESS)
        self.assertEqual(response.error_message, "Messages received successfully!!")
        self.assertEqual(len(response.message), 1)
        self.assertEqual(response.message[0].from_, sender_username)
        self.assertEqual(response.message[0].message, message_content)
    
    def test_logout(self):
        # Create an account and log in
        username = "test_user"
        password = "test_password"
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=username, password=password), None)
        session_id = self.client_service.Login(spec_pb2.LoginRequest(username=username, password=password), None).session_id

        # Log out
        request = spec_pb2.LogoutRequest(session_id=session_id)
        response = self.client_service.Logout(request, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.SUCCESS)
        self.assertEqual(response.error_message, "Logout successful!!")

    def test_delete_account(self):
        # Create an account and log in
        username = "test_user"
        password = "test_password"
        self.client_service.CreateAccount(spec_pb2.CreateAccountRequest(username=username, password=password), None)
        session_id = self.client_service.Login(spec_pb2.LoginRequest(username=username, password=password), None).session_id

        # Delete the account
        request = spec_pb2.DeleteAccountRequest(session_id=session_id)
        response = self.client_service.DeleteAccount(request, None)

        self.assertEqual(response.error_code, spec_pb2.StatusCode.SUCCESS)
        self.assertEqual(response.error_message, "Account deleted successfully!!")

if __name__ == '__main__':
    unittest.main()

    # Add more test methods for Send, ListUsers, ReceiveMessage, Logout, and DeleteAccount

if __name__ == '__main__':
    unittest.main()
