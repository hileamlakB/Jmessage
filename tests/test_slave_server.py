import unittest
from unittest.mock import MagicMock, patch
import spec_pb2
import spec_pb2_grpc
from slave_server import SlaveService, ClientServiceSlave, serve_slave_client, server_slave_master


class TestSlaveService(unittest.TestCase):
    def setUp(self):
        self.state = {
            'db_session': MagicMock(),
            'master_address': "localhost:50051",
            'slave_address': "localhost:50052",
            'slaves': [],
            'database_url': 'sqlite:///slave.db',
            'client_address': 'localhost:50053'
        }
        self.slave_service = SlaveService(db_session=self.state['db_session'],
                                          master_address=self.state['master_address'],
                                          state=self.state)

    def test_AcceptUpdates(self):
        update_data = MagicMock(spec=spec_pb2.UpdateData)
        with patch("slave_server.SlaveService.process_update_data") as mock_process_update_data:
            result = self.slave_service.AcceptUpdates(update_data, None)
            mock_process_update_data.assert_called_once_with(update_data)
            self.assertEqual(result.error_code, 0)

    def test_UpdateMaster(self):
        request = spec_pb2.UpdateMasterRequest(
            new_master_address="localhost:60051", new_master_id=2)
        with patch("slave_server.assign_new_master") as mock_assign_new_master:
            result = self.slave_service.UpdateMaster(request, None)
            mock_assign_new_master.assert_called_once_with(
                self.state, "localhost:60051", 2)
            self.assertEqual(result.error_code, 0)

    def test_UpdateSlaves(self):
        request = spec_pb2.UpdateSlavesRequest(update_data=MagicMock())
        with patch("pickle.loads") as mock_pickle_loads:
            new_slave = ("localhost:70051", 3)
            mock_pickle_loads.return_value = new_slave
            result = self.slave_service.UpdateSlaves(request, None)
            self.assertIn(new_slave, self.state['slaves'])
            self.assertEqual(result.error_code, 0)


class TestServeSlaveClient(unittest.TestCase):
    def test_serve_slave_client(self):
        with patch("grpc.server") as mock_server:
            state = {
                'db_session': MagicMock(),
                'master_address': "localhost:50051",
                'slave_address': "localhost:50052",
                'slaves': [],
                'database_url': 'sqlite:///slave.db',
                'client_address': 'localhost:50053'
            }
            serve_slave_client(state)
            mock_server.assert_called_once()


class TestServerSlaveMaster(unittest.TestCase):
    def test_server_slave_master(self):
        with patch("grpc.server") as mock_server:
            state = {
                'db_session': MagicMock(),
                'master_address': "localhost:50051",
                'slave_address': "localhost:50052",
                'slaves': [],
                'database_url': 'sqlite:///slave.db',
                'client_address': 'localhost:50053'
            }
            server_slave_master(state)
            mock_server.assert_called_once()


if __name__ == "__main__":
    unittest.main()
