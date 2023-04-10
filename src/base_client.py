import grpc
import spec_pb2
import spec_pb2_grpc
import time


class JarvesClientBase:
    def __init__(self, port, max_retries=2, retry_interval=1):
        self.user_session_id = ""
        self.port = port
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.channel = None
        self.stub = None
        return self.connect()

    def connect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.channel = grpc.insecure_channel(f'localhost:{self.port}')
                self.stub = spec_pb2_grpc.ClientAccountStub(self.channel)
                # Test the connection using a simple request like ListUsers
                response = self.stub.ListUsers(spec_pb2.Empty())
                if response:
                    print("Connection successful.")
                    break
            except grpc.RpcError as e:
                print(
                    f"Connection failed. Retrying in {self.retry_interval} seconds... Error: {e}")
                retries += 1
                time.sleep(self.retry_interval)
                self.channel = None
                self.stub = None
        else:
            print("Failed to establish connection after maximum retries.")

    def list_users(self):
        response = self.stub.ListUsers(spec_pb2.Empty())
        return response.user

    def create_account(self, username, password):
        response = self.stub.CreateAccount(
            spec_pb2.CreateAccountRequest(username=username, password=password))
        return response

    def login(self, username, password):
        response = self.stub.Login(
            spec_pb2.LoginRequest(username=username, password=password))
        return response

    def send_message(self, to, message):
        response = self.stub.Send(
            spec_pb2.SendRequest(session_id=self.user_session_id, message=message, to=to))
        return response

    def logout(self):
        response = self.stub.Logout(
            spec_pb2.DeleteAccountRequest(session_id=self.user_session_id))
        return response

    def delete_account(self):
        response = self.stub.DeleteAccount(
            spec_pb2.DeleteAccountRequest(session_id=self.user_session_id))
        return response

    def get_chat(self, recipient):
        msgs = self.stub.GetChat(
            spec_pb2.ChatRequest(session_id=self.user_session_id, username=recipient))
        return msgs

    def receive_messages(self):
        msgs = self.stub.GetMessages(
            spec_pb2.ReceiveRequest(session_id=self.user_session_id))
        return msgs

    def acknowledge_received_messages(self, message_ids):
        ack_response = self.stub.AcknowledgeReceivedMessages(
            spec_pb2.AcknowledgeRequest(session_id=self.user_session_id, message_ids=message_ids))
        return ack_response
