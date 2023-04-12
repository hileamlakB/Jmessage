import grpc
import threading
import time
import spec_pb2_grpc
import spec_pb2


class reconnect_on_error:
    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        def wrapped_method(*args, **kwargs):
            try:
                return self.method(instance, *args, **kwargs)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    print("Server is unavailable. Trying to reconnect...")
                    instance.connect()
                    return self.method(instance, *args, **kwargs)
                else:
                    raise
        return wrapped_method


class JarvesClientBase:
    def __init__(self, addresses, max_retries=2, retry_interval=1):
        self.user_session_id = ""
        self.addresses = addresses
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.channel = None
        self.stub = None
        self.lock = threading.Lock()
        self.connect()

    def exit_(self):
        pass

    def connect(self):

        with self.lock:
            # Check the connection using a simple request like ListUsers
            try:
                response = self.stub.ListUsers(spec_pb2.Empty())
                if response:
                    print("Connection is active")
                    return
            except (AttributeError, grpc.RpcError) as e:
                pass

            if len(self.addresses) == 0:
                print("No server is available.")
                self.exit_()

            tried = set()
            retries = 0
            success = False
            while retries < self.max_retries:
                try:
                    self.channel = grpc.insecure_channel(self.addresses[0])
                    self.stub = spec_pb2_grpc.ClientAccountStub(self.channel)
                    response = self.stub.ListUsers(spec_pb2.Empty())
                    if response:
                        success = True
                        print("Connected to the server")
                        break
                except grpc.RpcError as e:
                    if (e.code() == grpc.StatusCode.UNIMPLEMENTED):
                        # we are probably talking to a slave so move the address to the end
                        if (self.addresses[0] in tried):
                            # we have visted all the addresses and nodes are not responding
                            # so we can exit
                            self._exit()
                            return

                        tried.add(self.addresses[0])
                        self.addresses.append(self.addresses.pop(0))
                    else:
                        print(
                            f"Connection failed. Retrying in {self.retry_interval} seconds... Error: {e}")
                        retries += 1
                    time.sleep(self.retry_interval)

            if not success:
                print("Failed to establish connection after maximum retries.")
                # if reachingout to the server multiple times doesn't get response
                # delete this address as it is usless
                self.addresses.pop(0)
                return self.connect()

    @reconnect_on_error
    def list_users(self):
        response = self.stub.ListUsers(spec_pb2.Empty())
        return response.user

    @reconnect_on_error
    def create_account(self, username, password):
        response = self.stub.CreateAccount(
            spec_pb2.CreateAccountRequest(username=username, password=password))
        return response

    @reconnect_on_error
    def login(self, username, password):
        response = self.stub.Login(
            spec_pb2.LoginRequest(username=username, password=password))
        return response

    @reconnect_on_error
    def send_message(self, to, message):
        response = self.stub.Send(
            spec_pb2.SendRequest(session_id=self.user_session_id, message=message, to=to))
        return response

    @reconnect_on_error
    def logout(self):
        response = self.stub.Logout(
            spec_pb2.DeleteAccountRequest(session_id=self.user_session_id))
        return response

    @reconnect_on_error
    def delete_account(self):
        response = self
