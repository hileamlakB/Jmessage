import unittest
import grpc
from concurrent import futures
from unittest.mock import MagicMock, patch

import spec_pb2
import spec_pb2_grpc
from master_server import ClientService, MasterService, serve_master_client, serve_master_slave


class TestClientService(unittest.TestCase):
    def setUp(self):
        self.client_service = ClientService()

    def test_CreateAccount_success(self):
        with patch("master_server.UserManager.create_account") as mock_create_account:
            mock_create_account.return_value = True
            result = self.client_service.CreateAccount(
                spec_pb2.AccountRequest(username="testuser", password="testpass"))
            self.assertEqual(result.status, spec_pb2.Status.SUCCESS)

    def test_CreateAccount_failure(self):
        with patch("master_server.UserManager.create_account") as mock_create_account:
            mock_create_account.return_value = False
            result = self.client_service.CreateAccount(
                spec_pb2.AccountRequest(username="testuser", password="testpass"))
            self.assertEqual(result.status, spec_pb2.Status.FAILURE)

    def test_Login_success(self):
        with patch("master_server.UserManager.login") as mock_login:
            mock_login.return_value = True
            result = self.client_service.Login(spec_pb2.LoginRequest(
                username="testuser", password="testpass"))
            self.assertEqual(result.status, spec_pb2.Status.SUCCESS)

    def test_Login_failure(self):
        with patch("master_server.UserManager.login") as mock_login:
            mock_login.return_value = False
            result = self.client_service.Login(spec_pb2.LoginRequest(
                username="testuser", password="testpass"))
            self.assertEqual(result.status, spec_pb2.Status.FAILURE)

    def test_Send(self):
        with patch("master_server.MessageManager.send_message") as mock_send_message:
            mock_send_message.return_value = True
            result = self.client_service.Send(spec_pb2.Message(
                sender="testuser", content="Hello, World!"))
            self.assertEqual(result.status, spec_pb2.Status.SUCCESS)


class TestMasterService(unittest.TestCase):
    def setUp(self):
        self.master_service = MasterService()

    def test_RegisterSlave(self):
        with patch("master_server.SlaveManager.register_slave") as mock_register_slave:
            mock_register_slave.return_value = True
            result = self.master_service.RegisterSlave(
                spec_pb2.SlaveRegistration(hostname="slave1.example.com", port=12345))
            self.assertEqual(result.status, spec_pb2.Status.SUCCESS)

    def test_HeartBeat(self):
        with patch("master_server.SlaveManager.heartbeat") as mock_heartbeat:
            mock_heartbeat.return_value = True
            result = self.master_service.HeartBeat(
                spec_pb2.HeartBeatRequest(slave_id=1))
            self.assertEqual(result.status, spec_pb2.Status.SUCCESS)

    def test_CheckMaster(self):
        with patch("master_server.SlaveManager.is_master_alive") as mock_is_master_alive:
            mock_is_master_alive.return_value = True
            result = self.master_service.CheckMaster(spec_pb2.Empty())
            self.assertEqual(result.status, spec_pb2.Status.SUCCESS)


class TestServeMasterClient(unittest.TestCase):
    def test_serve_master_client(self):
        with patch("grpc.server") as mock_server:
            serve_master_client()
            mock_server.assert_called_once()


class TestServeMasterSlave(unittest.TestCase):
    def test_serve_master_slave(self):
        with patch("grpc.server") as mock_server:
            serve_master_slave()
            mock_server.assert_called_once()


if __name__ == "__main__":
    unittest.main()
