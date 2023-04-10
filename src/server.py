from concurrent import futures
import logging
import uuid
import queue

import grpc
import spec_pb2
import spec_pb2_grpc
from utils import StatusCode, StatusMessages

from models import UserModel, MessageModel, DeletedMessageModel, init_db, get_session_factory
from sqlalchemy.orm import scoped_session
from sqlalchemy import or_, and_
from google.protobuf.timestamp_pb2 import Timestamp

import pickle
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import threading
import time
import queue


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


class ClientServiceSlave(spec_pb2_grpc.ClientAccountServicer):
    
    
    

    def CreateAccount(self, request, context):
        status_code = StatusCode.NOT_MASTER
        status_message = StatusMessages.get_error_message(status_code)
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)


    def ListUsers(self, request, context):
        users = spec_pb2.Users()
        return users
        
    def Login(self, request, context):
        """Define an RPC for logging in to an account
        """
        status_code = StatusCode.NOT_MASTER
        status_message = StatusMessages.get_error_message(status_code)
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def Send(self, request, context):
        """Define an RPC for sending a message to a recipient
        """
        status_code = StatusCode.NOT_MASTER
        status_message = StatusMessages.get_error_message(status_code)
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)

    def GetMessages(self, request, context):
        """Define an RPC for receiving messages
        rpc SubscribeMessage(ReceiveRequest) returns (stream Message);

        Define an RPC for receiving messages
        """
        msgs = spec_pb2.Messages()
        return msgs

    def GetChat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        msgs = spec_pb2.Messages()
        return msgs

    def AcknowledgeReceivedMessages(self, request, context):
        """Define an RPC for receiving messages
        """
        status_code = StatusCode.NOT_MASTER
        status_message = StatusMessages.get_error_message(status_code)
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)


    def DeleteAccount(self, request, context):
        """Define an RPC for deleting an account
        """
        status_code = StatusCode.NOT_MASTER
        status_message = StatusMessages.get_error_message(status_code)
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)


    def Logout(self, request, context):
        """Define an RPC for logging out of an account
        """
        status_code = StatusCode.NOT_MASTER
        status_message = StatusMessages.get_error_message(status_code)
        return spec_pb2.ServerResponse(error_code=status_code, error_message=status_message)




def fetch_all_data_from_orm(connection):
    data = {}
    Session = sessionmaker(bind=connection)
    session = Session()

    # Get the list of classes defined in your ORM
    # Replace with your actual ORM classes
    orm_classes = [UserModel, MessageModel, DeletedMessageModel]

    for orm_class in orm_classes:
        table_name = orm_class.__tablename__
        table_data = session.query(orm_class).all()
        data[table_name] = table_data

    session.close()
    return data


class MasterService(spec_pb2_grpc.MasterServiceServicer):
    def __init__(self, slaves, db_engine):
        super().__init__()
        self.slaves = slaves
        self.db_engine = db_engine

    def RegisterSlave(self, request, context):
        slave_id = request.slave_id
        self.slaves.append(slave_id)
        
        
        # Fetch and pickle the data from ORM objects
        with self.db_engine.begin() as connection:
            # Implement this function to fetch data from ORM objects
            data = fetch_all_data_from_orm(connection)
            pickled_data = pickle.dumps(data)

        other_slaves = [slave for slave in self.slaves if slave != slave_id]

        response = spec_pb2.RegisterSlaveResponse(
            error_code=0,
            error_message="",
            pickled_db=pickled_data,
            other_slaves=other_slaves
        )
        print("Slave {} registered {} resp {}".format(slave_id, request.slave_address, response))

        
        return response


class SlaveService(spec_pb2_grpc.SlaveServiceServicer):
    def __init__(self, db_session, master_addres):
        self.db_session = db_session
        self.master_address = master_address

    def AcceptUpdates(self, request, context):
        update_data = request.update_data
        self.process_update_data(update_data)

        response = spec_pb2.ServerResponse(
            error_code=0,
            error_message=""
        )
        return response

    def process_update_data(self, update_data):
        # Add your implementation for processing the update_data
        session = scoped_session(self.db_session)

        data = pickle.loads(update_data)
        action, obj = data
        if action == 'add':
            session.add(obj)
        elif action == 'delete':
            session.delete(obj)
        elif action == 'update':
            session.merge(obj)
        session.commit()


def serve_slave_client(db_session, address, master_address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spec_pb2_grpc.add_ClientAccountServicer_to_server(
        ClientServiceSlave(), server)
    server.add_insecure_port(address)
    server.start()
    print("Server started, listening on ", address)
    return server

def serve_master_client(db_session, address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spec_pb2_grpc.add_ClientAccountServicer_to_server(
        ClientService(db_session=db_session), server)
    server.add_insecure_port(address)
    server.start()
    print("Client server started, listening on " + address)
    return server

# internal channel for master to communicate with slave
def serve_master_slave(address, db_engine):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spec_pb2_grpc.add_MasterServiceServicer_to_server(
        MasterService([], db_engine=db_engine), server)
    # spec_pb2_grpc.add_SlaveServiceServicer_to_server(
    #     SlaveService([]), server)
    server.add_insecure_port(address)
    server.start()
    print("Master server started, listening on " + address)
    return server

def server_slave_master(db_session, master_address, address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spec_pb2_grpc.add_SlaveServiceServicer_to_server(
        SlaveService(db_session=db_session, master_addres=master_address), server)
    
    server.add_insecure_port(address)
    server.start()
    print("Master server started, listening on " + address)
    return server

def get_update_data(update_queue):
    try:
        data = update_queue.get(block=False)
        return data
    except queue.Empty:
        return None


def update_slaves(slaves, update_queue):
    while True:
        # Fetch the update data here
        update_data = get_update_data(update_queue)

        if update_data is not None:
            # Iterate through each slave and send updates
            for slave_address in slaves:
                try:
                    with grpc.insecure_channel(slave_address) as channel:
                        stub = spec_pb2_grpc.SlaveServiceStub(channel)
                        accept_updates_request = spec_pb2.AcceptUpdatesRequest(
                            update_data=update_data)
                        response = stub.AcceptUpdates(accept_updates_request)
                except Exception as e:
                    print("Error while sending updates to slave: " + str(e))
        time.sleep(2)


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Start a chat server as a master or a slave.")
    parser.add_argument("server_id", help="Unique server ID.")
    parser.add_argument(
        "type", choices=["master", "slave"], help="Server type: master or slave.")
    parser.add_argument(
        "client_address", help="Server address to communicate client in the format < host > : < port >"
    )
    parser.add_argument(
        "internal_address", help="Server address to communicate internally in the format < host > : < port >"
    )
    parser.add_argument(
        "--master_address", help="Master server address (required for slave servers).")

    args = parser.parse_args()

    server_id = args.server_id
    server_type = args.type
    client_address = args.client_address
    internal_address = args.internal_address
    master_address = args.master_address

    if server_type == "slave" and master_address is None:
        parser.error("Slave servers require the --master_address option.")

    

    if server_type == 'master':
        database_url = f'sqlite:///chat_{server_id}.db'
        database_engine = init_db(database_url)
        
        slaves = []
        update_queue = queue.Queue()
        # start internal server for master
        # slave communication
        master_server = serve_master_slave(address=internal_address, 
                                           db_engine=database_engine)

        # Start a separate thread to send updates to slaves
        update_thread = threading.Thread(
            target=update_slaves, args=(slaves, update_queue))
        update_thread.start()

        SessionFactory = get_session_factory(database_engine)
        logging.basicConfig()
        clinet_server = serve_master_client(db_session=SessionFactory, address=client_address)

        master_server.wait_for_termination()
        clinet_server.wait_for_termination()

    else:
        database_url = f'sqlite:///chat_{server_id}.db'
        database_engine = init_db(database_url, drop_tables=True)
        
        SessionFactory = get_session_factory(database_engine)
        logging.basicConfig()
        
        # start internal server for slave
        server_slave_master(db_session=SessionFactory, master_address=master_address, address=internal_address)
        
        # send message to the masters registe method
        with grpc.insecure_channel(master_address) as channel:
            stub = spec_pb2_grpc.MasterServiceStub(channel)
            register_slave_request = spec_pb2.RegisterSlaveRequest(
                slave_id=server_id, slave_address=internal_address)
            response = stub.RegisterSlave(register_slave_request)
            print('slave registered: ', response)
            # update database with the master data
        
        
        clinet_server = serve_slave_client(db_session=SessionFactory, address=client_address, master_address=master_address)
        clinet_server.wait_for_termination()

        
        
