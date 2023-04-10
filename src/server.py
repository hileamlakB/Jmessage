from concurrent import futures
import logging
import uuid

import grpc
import spec_pb2
import spec_pb2_grpc
from utils import StatusCode, StatusMessages

from models import UserModel, MessageModel, DeletedMessageModel, init_db, get_session_factory
from sqlalchemy.orm import scoped_session
from sqlalchemy import or_, and_
from google.protobuf.timestamp_pb2 import Timestamp


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

    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        # self.all_users = {
        #     # username: User
        # }
        # self.session_map = {
        #     # session_id: User
        # }

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
            new_user = UserModel(username=request.username,
                                 password=request.password)
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

        session_id = None
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
        session = scoped_session(self.db_session)
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
        session.remove()

        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def ListUsers(self, request, context):
        context.set_code(grpc.StatusCode.OK)
        users = spec_pb2.Users()

        session = scoped_session(self.db_session)
        all_users = session.query(UserModel).all()

        for user in all_users:
            user_ = users.user.add()
            user_.username = user.username
            user_.status = "online" if user.logged_in else "offline"

        # Remove any remaining session
        session.remove()

        return users

    def GetMessages(self, request, context):
        context.set_code(grpc.StatusCode.OK)

        msgs = spec_pb2.Messages()

        session = scoped_session(self.db_session)
        user = session.query(UserModel).filter_by(
            s50051ession_id=request.session_id).first()

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
                    msg.message_id = message.id
                    message.is_received = True

                session.commit()
                msgs.error_code = StatusCode.SUCCESS
                msgs.error_message = "Messages received successfully!!"

        session.remove()

        return msgs

    def AcknowledgeReceivedMessages(self, request, context):
        session = scoped_session(self.db_session)
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

                # stop deleting messages
                # Move the message to the deleted_messages table
                # deleted_message = DeletedMessageModel(
                #     sender_id=message.sender_id,
                #     receiver_id=message.receiver_id,
                #     content=message.content,
                #     is_received=message.is_received,
                #     original_message_id=message.id,
                # )
                # session.add(deleted_message)
                # session.delete(message)

            session.commit()
            status_code = StatusCode.SUCCESS
            status_message = "Messages acknowledged successfully!!"

        session.remove()

        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def Logout(self, request, context):
        session = scoped_session(self.db_session)
        user = session.query(UserModel).filter_by(
            session_id=request.session_id).first()

        if user is None:
            status = StatusCode.USER_NOT_LOGGED_IN
            status_message = StatusMessages.get_error_message(status)
        else:
            user.session_id = None
            user.logged_in = False
            session.commit()
            status = StatusCode.SUCCESS
            status_message = "Logout successful!!"

        session.remove()

        return spec_pb2.ServerResponse(error_code=status, error_message=status_message)

    def GetChat(self, request, context):
        context.set_code(grpc.StatusCode.OK)

        msgs = spec_pb2.Messages()

        session = scoped_session(self.db_session)
        user = session.query(UserModel).filter_by(
            session_id=request.session_id).first()

        if user is None:
            msgs.error_code = StatusCode.USER_NOT_LOGGED_IN
            msgs.error_message = StatusMessages.get_error_message(
                msgs.error_code)
        else:
            receiver = session.query(UserModel).filter_by(
                username=request.username).first()

            messages = session.query(MessageModel).filter(
                or_(
                    and_(MessageModel.sender_id == user.id,
                         MessageModel.receiver_id == receiver.id),
                    and_(MessageModel.sender_id == receiver.id,
                         MessageModel.receiver_id == user.id)
                )
            ).order_by(MessageModel.time_stamp).all()

            if len(messages) == 0:
                msgs.error_code = StatusCode.NO_MESSAGES
                msgs.error_message = StatusMessages.get_error_message(
                    msgs.error_code)
            else:
                for message in messages:
                    msg = msgs.message.add()
                    msg.from_ = message.sender.username
                    msg.message = message.content
                    msg.message_id = message.id
                    print(message.time_stamp)
                    timestamp_proto = Timestamp()
                    print(timestamp_proto)
                    timestamp_proto.FromDatetime(message.time_stamp)
                    msg.time_stamp.CopyFrom(timestamp_proto)
                    message.is_received = True

                session.commit()
                msgs.error_code = StatusCode.SUCCESS
                msgs.error_message = "Messages received successfully!!"

        session.remove()

        return msgs

    def DeleteAccount(self, request, context):
        session = scoped_session(self.db_session)
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

        session.remove()

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


def register_master(slaves):
    # should be used by the master server
    # to respond to slaves register requests
    # and add them to the slaves list
    # pickle sqlorm database and send it to the slave
    pass


def slave_adder_thread(slaves):
    while True:
        register_master(slaves)


def register_slave(master_address):
    # which should connect to 
    # the master thorugh grpc and register itself
    # after registering the server shoudl send a pickled version of
    # the current database, the slave then 
    # creates a new database based on the pickled database 
    # and starts the slave server
    # which does three things (starts two threads)
    # 1. for listenting from the server for updates
    # 2. for checking on the server (heartbeat)
    # 3. for connecting to the clients and tell them that it is a slave
    


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Start a chat server as a master or a slave.")
    parser.add_argument("server_id", help="Unique server ID.")
    parser.add_argument(
        "type", choices=["master", "slave"], help="Server type: master or slave.")
    parser.add_argument(
        "--master_address", help="Master server address (required for slave servers).")

    args = parser.parse_args()

    server_id = args.server_id
    server_type = args.type
    master_address = args.master_address

    if server_type == "slave" and master_address is None:
        parser.error("Slave servers require the --master_address option.")

    database_url = f'sqlite:///chat_{server_id}.db'
    database_engine = init_db(database_url)

    if server_type == 'master':
        SessionFactory = get_session_factory(database_engine)
        logging.basicConfig()
        serve(db_session=SessionFactory)
        slaves = []
        # start a slave adder thread
        # make sure slaves is lcoked when it is updated
    else:
        # if it is a slave
        # call the register method,
        # and then start the slave server
