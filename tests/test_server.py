import unittest
from unittest.mock import MagicMock

import spec_pb2
import spec_pb2_grpc

from server import ClientService, UserModel, init_db, get_session_factory
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestClientService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a temporary SQLite database for testing
        cls.engine = create_engine("sqlite:///:memory:")
        cls.session_factory = get_session_factory(cls.engine)
        init_db(cls.engine)

    def setUp(self):
        self.client_service = ClientService(db_session=self.session_factory)

    def test_create_account(self):
        username = "testuser"
        password = "testpassword"

        response = self.client_service.CreateAccount(
            spec_pb2.Account(username=username, password=password), MagicMock()
        )

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message,
                         "Account created successfully!!")

    def test_login(self):
        username = "testuser"
        password = "testpassword"

        response = self.client_service.Login(
            spec_pb2.LoginRequest(
                username=username, password=password), MagicMock()
        )

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message, "Login successful!!")
        self.assertIsNotNone(response.session_id)

    def test_send(self):
        username1 = "testuser"
        password1 = "testpassword"

        username2 = "testuser2"
        password2 = "testpassword2"

        session = scoped_session(self.session_factory)
        user1 = UserModel(username=username1,
                          password=password1, session_id="1234")
        user2 = UserModel(username=username2,
                          password=password2, session_id="5678")
        session.add(user1)
        session.add(user2)
        session.commit()

        response = self.client_service.Send(
            spec_pb2.SendMessageRequest(
                session_id="1234", to=username2, message="Hello!"), MagicMock()
        )

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message, "Message sent successfully!!")

    def test_list_users(self):
        response = self.client_service.ListUsers(
            spec_pb2.SessionIdRequest(session_id="1234"), MagicMock())

        self.assertEqual(len(response.user), 2)

    def test_get_messages(self):
        response = self.client_service.GetMessages(
            spec_pb2.SessionIdRequest(session_id="5678"), MagicMock())

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message,
                         "Messages received successfully!!")
        self.assertEqual(len(response.message), 1)

    def test_acknowledge_received_messages(self):
        session = scoped_session(self.session_factory)
        message_id = session.query(UserModel).filter_by(
            username="testuser").first().sent_messages[0].id
        session.remove()

        response = self.client_service.AcknowledgeReceivedMessages(
            spec_pb2.AcknowledgeReceivedMessagesRequest(
                session_id="5678", message_ids=[message_id]), MagicMock()
        )

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message,
                         "Messages acknowledged successfully!!")

    def test_logout(self):
        response = self.client_service.Logout(
            spec_pb2.SessionIdRequest(session_id="1234"), MagicMock())

        self.assertEqual(response.error_message, "Logout successful!!")

    def test_delete_account(self):
        session = scoped_session(self.session_factory)
        user = session.query(UserModel).filter_by(username="testuser").first()
        session_id = user.session_id
        session.remove()

        response = self.client_service.DeleteAccount(
            spec_pb2.SessionIdRequest(session_id=session_id), MagicMock())

        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_message,
                         "Account deleted successfully!!")

        session = scoped_session(self.session_factory)
        deleted_user = session.query(UserModel).filter_by(
            username="testuser").first()
        session.remove()
        self.assertIsNone(deleted_user)


if __name__ == "__main__":
    unittest.main()
