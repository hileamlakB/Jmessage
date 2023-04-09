import unittest
# Replace with your server file name
from your_server_file import User, Message, Session, Base, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)  # Create the tables

    @classmethod
    def tearDownClass(cls):
        # Drop the tables after all tests are done
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.session = sessionmaker(bind=self.engine)()  # Create a new session for each test

    def tearDown(self):
        self.session.rollback()  # Rollback any changes made during the test
        self.session.close()  # Close the session

    def test_create_and_retrieve_user(self):
        username = "test_user"
        password = "test_password"

        # Create a user
        new_user = User(username=username, password=password)
        self.session.add(new_user)
        self.session.commit()

        # Retrieve the user from the database
        retrieved_user = self.session.query(
            User).filter_by(username=username).one()

        self.assertEqual(retrieved_user.username, username)
        self.assertEqual(retrieved_user.password, password)

    def test_create_and_retrieve_message(self):
        from_username = "sender"
        to_username = "receiver"
        content = "Test message"

        # Create a message
        new_message = Message(from_username=from_username,
                              to_username=to_username, content=content)
        self.session.add(new_message)
        self.session.commit()

        # Retrieve the message from the database
        retrieved_message = self.session.query(Message).filter_by(
            from_username=from_username, to_username=to_username).one()

        self.assertEqual(retrieved_message.from_username, from_username)
        self.assertEqual(retrieved_message.to_username, to_username)
        self.assertEqual(retrieved_message.content, content)

    def test_update_user(self):
        username = "test_user"
        password = "test_password"
        new_password = "new_password"

        # Create a user
        new_user = User(username=username, password=password)
        self.session.add(new_user)
        self.session.commit()

        # Update the user's password
        user_to_update = self.session.query(
            User).filter_by(username=username).one()
        user_to_update.password = new_password
        self.session.commit()

        # Retrieve the updated user
        updated_user = self.session.query(
            User).filter_by(username=username).one()
        self.assertEqual(updated_user.password, new_password)

    def test_delete_user(self):
        username = "test_user"
        password = "test_password"

        # Create a user
        new_user = User(username=username, password=password)
        self.session.add(new_user)
        self.session.commit()

        # Delete the user
        user_to_delete = self.session.query(
            User).filter_by(username=username).one()
        self.session.delete(user_to_delete)
        self.session.commit()

        # Try to retrieve the deleted user
        deleted_user = self.session.query(
            User).filter_by(username=username).first()
        self.assertIsNone(deleted_user)

    def test_update_message(self):
        from_username = "sender"
        to_username = "receiver"
        content = "Test message"
        new_content = "Updated message"

        # Create a message
        new_message = Message(from_username=from_username,
                              to_username=to_username, content=content)
        self.session.add(new_message)
        self.session.commit()

        # Update the message content
        message_to_update = self.session.query(Message).filter_by(
            from_username=from_username, to_username=to_username).one()
        message_to_update.content = new_content
        self.session.commit()

        # Retrieve the updated message
        updated_message = self.session.query(Message).filter_by(
            from_username=from_username, to_username=to_username).one()
        self.assertEqual(updated_message.content, new_content)

    def test_delete_message(self):
        from_username = "sender"
        to_username = "receiver"
        content = "Test message"

        # Create a message
        new_message = Message(from_username=from_username,
                              to_username=to_username, content=content)
        self.session.add(new_message)
        self.session.commit()

        # Delete the message
        message_to_delete = self.session.query(Message).filter_by(
            from_username=from_username, to_username=to_username).one()
        self.session.delete(message_to_delete)
        self.session.commit()

        # Try to retrieve the deleted message
        deleted_message = self.session.query(Message).filter_by(
            from_username=from_username, to_username=to_username).first()
        self.assertIsNone(deleted_message)

    def test_count_users(self):
        # Create multiple users
        usernames = ["user1", "user2", "user3"]
        for username in usernames:
            user = User(username=username, password="password")
            self.session.add(user)

        self.session.commit()

        # Count the number of users in the database
        user_count = self.session.query(User).count()
        self.assertEqual(user_count, len(usernames))

    def test_count_messages(self):
        from_username = "sender"
        to_usernames = ["receiver1", "receiver2", "receiver3"]
        content = "Test message"

        # Create multiple messages
        for to_username in to_usernames:
            message = Message(from_username=from_username,
                              to_username=to_username, content=content)
            self.session.add(message)

        self.session.commit()

        # Count the number of messages in the database
        message_count = self.session.query(Message).count()
        self.assertEqual(message_count, len(to_usernames))

    def test_filter_messages(self):
        from_username = "sender"
        to_usernames = ["receiver1", "receiver2", "receiver3"]
        content = "Test message"

        # Create multiple messages
        for to_username in to_usernames:
            message = Message(from_username=from_username,
                              to_username=to_username, content=content)
            self.session.add(message)

        self.session.commit()

        # Filter messages by sender and receiver
        filtered_messages = self.session.query(Message).filter_by(
            from_username=from_username, to_username=to_usernames[0]).all()
        self.assertEqual(len(filtered_messages), 1)
        self.assertEqual(filtered_messages[0].to_username, to_usernames[0])


    # Add more test methods for updating and deleting users and messages, and for any additional methods in the User and Message classes
if __name__ == '__main__':
    unittest.main()
