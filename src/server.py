from concurrent import futures
import logging
import uuid

import grpc
import spec_pb2
import spec_pb2_grpc
from src.utils import StatusCode, StatusMessages

from .models import UserModel, MessageModel, DeletedMessageModel, init_db, get_session_factory
from sqlalchemy.orm import scoped_session


# represents a single client
class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.messages = []
        self.login_status = {
            "logged_in": False,
            "session_id": None,
            "subscription_stream": None
        }

    def login(self, session_id):
        self.login_status["logged_in"] = True
        self.login_status["session_id"] = session_id

    def logout(self):
        self.login_status["logged_in"] = False
        self.login_status["session_id"] = None

    def is_logged_in(self):
        return self.login_status["logged_in"]

    def get_session_id(self):
        return self.login_status["session_id"]

    def add_message(self, message):
        self.messages.append(message)


class ClientService(spec_pb2_grpc.ClientAccountServicer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = kwargs['db_session']
        self.all_users = {
            # username: User
        }
        self.session_map = {
            # session_id: User
        }

    def CreateAccount(self, request, context):

        session = scoped_session(self.db_session)
        context.set_code(grpc.StatusCode.OK)

        user_exists = session.query(UserModel).filter_by(
            username=request.username).scalar()
        if user_exists:
            status_code = StatusCode.USER_NAME_EXISTS
            status_message = StatusMessages.get_error_message(status_code)
        else:
            # create a new user
            new_user = User(request.username, request.password)
            session.add(new_user)
            session.commit()
            status_code = StatusCode.SUCCESS
            status_message = "Account created successfully!!"

        session.remove()
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def Login(self, request, context):

        context.set_code(grpc.StatusCode.OK)
        session = scoped_session(self.db_session)
        user = session.query(UserModel).filter_by(
            username=request.username).first()

        if user is None:
            status_code = StatusCode.USER_DOESNT_EXIST
            status_message = StatusMessages.get_error_message(status_code)
        else:
            if user.password != request.password:
                status_code = StatusCode.INCORRECT_PASSWORD
                status_message = StatusMessages.get_error_message(status_code)
            else:
                session_id = self.GenerateSessionID()
                user.logged_in = True
                user.session_id = session_id
                session.commit()

                status_code = StatusCode.SUCCESS
                status_message = "Login successful!!"
                session_id = session_id

        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message, session_id=session_id)

    def Send(self, request, context):

        context.set_code(grpc.StatusCode.OK)

        session_id = request.session_id
        session = self.scoped_session()
        user = session.query(UserModel).filter_by(
            session_id=session_id).first()

        if user is None:
            status_code = StatusCode.USER_NOT_LOGGED_IN
            status_message = StatusMessages.get_error_message(status_code)
        else:
            receiver = session.query(UserModel).filter_by(
                username=request.to).first()

            if receiver is None:
                status_code = StatusCode.RECEIVER_DOESNT_EXIST
                status_message = StatusMessages.get_error_message(status_code)
            else:
                msg = MessageModel(
                    sender_id=user.id,
                    receiver_id=receiver.id,
                    content=request.message
                )
                session.add(msg)
                session.commit()

                status_code = StatusCode.SUCCESS
                status_message = "Message sent successfully!!"

        # Remove any remaining session
        self.scoped_session.remove()

        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def ListUsers(self, request, context):
        context.set_code(grpc.StatusCode.OK)
        users = spec_pb2.Users()

        session = self.scoped_session()
        all_users = session.query(UserModel).all()

        for user in all_users:
            user_ = users.user.add()
            user_.username = user.username
            user_.status = "online" if user.is_logged_in else "offline"

        # Remove any remaining session
        self.scoped_session.remove()

        return users

    def GetMessages(self, request, context):
        context.set_code(grpc.StatusCode.OK)

        msgs = spec_pb2.Messages()

        session = self.scoped_session()
        user = session.query(UserModel).filter_by(
            session_id=request.session_id).first()

        if user is None:
            msgs.error_code = StatusCode.USER_NOT_LOGGED_IN
            msgs.error_message = StatusMessages.get_error_message(
                msgs.error_code)
        else:
            messages = session.query(MessageModel).filter_by(
                receiver_id=user.id, is_received=False).all()

            if len(messages) == 0:
                msgs.error_code = StatusCode.NO_MESSAGES
                msgs.error_message = StatusMessages.get_error_message(
                    msgs.error_code)
            else:
                for message in messages:
                    msg = msgs.message.add()
                    msg.from_ = message.sender.username
                    msg.message = message.content
                    msg.id = message.id
                    message.is_received = True

                session.commit()
                msgs.error_code = StatusCode.SUCCESS
                msgs.error_message = "Messages received successfully!!"

        self.scoped_session.remove()

        return msgs

    def AcknowledgeReceivedMessages(self, request, context):
        session = self.scoped_session()
        user = session.query(UserModel).filter_by(
            session_id=request.session_id).first()

        if user is None:
            status_code = StatusCode.USER_NOT_LOGGED_IN
            status_message = StatusMessages.get_error_message(status_code)
        else:
            messages = session.query(MessageModel).filter(
                MessageModel.id.in_(request.message_ids),
                MessageModel.receiver_id == user.id
            ).all()

            for message in messages:
                message.is_received = True

                # Move the message to the deleted_messages table
                deleted_message = DeletedMessageModel(
                    sender_id=message.sender_id,
                    receiver_id=message.receiver_id,
                    content=message.content,
                    is_received=message.is_received,
                    original_message_id=message.id,
                )
                session.add(deleted_message)
                session.delete(message)

            session.commit()
            status_code = StatusCode.SUCCESS
            status_message = "Messages acknowledged successfully!!"

        self.scoped_session.remove()

        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def Logout(self, request, context):
        session = self.scoped_session()
        user = session.query(UserModel).filter_by(
            session_id=request.session_id).first()

        if user is None:
            status = StatusCode.USER_NOT_LOGGED_IN
            status_message = StatusMessages.get_error_message(status)
        else:
            user.session_id = None
            session.commit()
            status = StatusCode.SUCCESS
            status_message = "Logout successful!!"

        self.scoped_session.remove()

        return spec_pb2.ServerResponse(error_code=status, error_message=status_message)

    def DeleteAccount(self, request, context):
        session = self.scoped_session()
        user = session.query(UserModel).filter_by(
            session_id=request.session_id).first()

        if user is None:
            status_code = StatusCode.USER_NOT_LOGGED_IN
            status_message = StatusMessages.get_error_message(status_code)
        else:
            # Move user's messages to deleted_messages table
            messages_to_delete = session.query(MessageModel).filter(
                MessageModel.receiver_id == user.id
            ).all()

            for message in messages_to_delete:
                deleted_message = DeletedMessageModel(
                    sender_id=message.sender_id,
                    receiver_id=message.receiver_id,
                    content=message.content,
                    is_received=message.is_received,
                    original_message_id=message.id,
                )
            session.add(deleted_message)
            session.delete(message)

            # Delete user
            session.delete(user)
            session.commit()

            status_code = StatusCode.SUCCESS
            status_message = "Account deleted successfully!!"

        self.scoped_session.remove()

        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    @staticmethod
    def GenerateSessionID():
        return str(uuid.uuid4())


def serve(db_session):
    port = '2625'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spec_pb2_grpc.add_ClientAccountServicer_to_server(
        ClientService(db_session=db_session), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    import sys
    server_id = sys.argv[1]
    database_url = f'sqlite:///chat_{server_id}.db'
    database_engine = init_db(database_url)
    SessionFactory = get_session_factory(database_engine)
    logging.basicConfig()
    serve(db_session=SessionFactory)
