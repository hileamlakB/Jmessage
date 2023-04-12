import unittest
import grpc
import spec_pb2
import spec_pb2_grpc

from slave_server import SlaveServer
from master_server import MasterServer


class TestServer(unittest.TestCase):

    def test_slave(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = spec_pb2_grpc.SlaveServiceStub(channel)

            response = stub.Connect(spec_pb2.Empty())
            self.assertEqual(response.status, 1)

            response = stub.SendMessage(spec_pb2.Message(
                sender='test_user', content='test message'))
            self.assertEqual(response.status, 1)

    def test_master(self):
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = spec_pb2_grpc.MasterServiceStub(channel)

            response = stub.Connect(spec_pb2.Empty())
            self.assertEqual(response.status, 1)

            response = stub.SendMessage(spec_pb2.Message(
                sender='test_user', content='test message'))
            self.assertEqual(response.status, 1)

    def test_client(self):
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = spec_pb2_grpc.ClientServiceStub(channel)

            response = stub.Connect(spec_pb2.Empty())
            self.assertEqual(response.status, 1)

            response = stub.SendMessage(spec_pb2.Message(
                sender='test_user', content='test message'))
            self.assertEqual(response.status, 1)


if __name__ == '__main__':
    master_server = MasterServer('50052', '50053')
    slave_server = SlaveServer('50051', 'localhost:50052')
    master_server.start()
    slave_server.start()

    # wait for servers to start
    import time
    time.sleep(1)

    client_channel = grpc.insecure_channel('localhost:50053')
    client_stub = spec_pb2_grpc.ClientServiceStub(client_channel)

    # create a test user
    response = client_stub.CreateUser(spec_pb2.CreateUserRequest(
        username='test_user', password='test_password'))
    assert response.status == 1

    unittest.main(exit=False)

    # stop servers
    slave_server.stop()
    master_server.stop()
