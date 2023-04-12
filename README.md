# N-Failstop Fault Tolerant Chat Application Documentation

## Overview

This chat application is designed to be resilient against up to N failstop faults. It uses a master-slave architecture to ensure fault tolerance and relies on the gRPC protocol for communication between its components. This documentation provides a comprehensive overview of the application's structure and functionality, including file organization and protocol buffer definitions.

## File Structure

The source code is organized as follows:

├── src
│ ├── base_client.py
│ ├── gui_client.py
│ ├── master_server.py
│ ├── models.py
│ ├── server.py
│ ├── slave_server.py
│ ├── spec_pb2_grpc.py
│ ├── spec_pb2.py
│ ├── spec_pb2.pyi
│ ├── spec.proto
│ ├── terminal_client.py
│ └── utils.py
├── tests
│ ├── test_base_client.py
│ ├── test_client.py
│ ├── test_database.py
│ └── test_server.py

### src/

- `base_client.py`: Contains the BaseClient class, which is a generic chat client implementation.
- `gui_client.py`: Extends the BaseClient class to create a GUI-based chat client.
- `__init__.py`: Indicates that this folder is a package.
- `master_server.py`: Implements the master server logic.
- `models.py`: Contains the data models used in the application, such as User and Message.
- `__pycache__`: Stores the compiled Python files.
- `server.py`: Contains the main server logic, shared between the master and slave servers.
- `slave_server.py`: Implements the slave server logic.
- `spec_pb2_grpc.py`: Generated gRPC code for the services defined in the spec.proto file.
- `spec_pb2.py`: Generated code from the spec.proto file for the message types.
- `spec_pb2.pyi`: Generated stub file for spec_pb2.py.
- `spec.proto`: Protocol buffer definition file for the application's gRPC services and message types.
- `terminal_client.py`: Extends the BaseClient class to create a terminal-based chat client.
- `utils.py`: Contains utility functions used throughout the application.

### tests/

- `test_base_client.py`: Unit tests for the base_client.py file.
- `test_client.py`: Unit tests for the gui_client.py and terminal_client.py files.
- `test_database.py`: Unit tests for the models.py file.
- `test_server.py`: Unit tests for the master_server.py and slave_server.py files.

## Protocol Buffer Definitions

The application uses Protocol Buffers (protobuf) to define its gRPC services and message types. The `spec.proto` file contains the following service and message definitions:

### ClientAccount

This service handles communication between clients and servers for user account management and messaging.

#### RPCs

- `CreateAccount`: Creates a new user account.
- `ListUsers`: Lists all users in the database.
- `Login`: Logs in to a user account.
- `Send`: Sends a message to another user.
- `GetMessages`: Retrieves messages for the logged-in user.
- `GetChat`: Retrieves messages between the logged-in user and another user.
- `AcknowledgeReceivedMessages`: Acknowledges the receipt of messages by the client.
- `DeleteAccount`: Deletes a user account.
- `Logout`: Logs out of a user account.

#### Messages

- `CreateAccountRequest`: Request message for creating a user account

* `ServerResponse`: Response message for server to send back to the client.
* `AcknowledgeReceivedMessagesRequest`: Request message for acknowledging received messages.
* `LoginRequest`: Request message for logging in.
* `SendRequest`: Request message for sending a message.
* `ReceiveRequest`: Request message for receiving messages.
* `ChatRequest`: Request message for getting chat messages between two users.
* `DeleteAccountRequest`: Request message for deleting an account.
* `Message`: Message object containing sender, content, ID, and timestamp.
* `Messages`: Response message containing a list of messages.
* `Empty`: Empty message used for certain RPC calls.
* `User`: User object containing username and status.
* `Users`: Response message containing a list of users.

### MasterService

This service handles communication between the master server and slave servers.

#### RPCs

- `RegisterSlave`: Registers a slave server.
- `HeartBeat`: Periodic check-in by a slave server to the master.
- `CheckMaster`: Checks the current status of the master server.

#### Messages

- `RegisterSlaveRequest`: Request message for registering a slave server.
- `RegisterSlaveResponse`: Response message for registering a slave server.
- `Ack`: Acknowledgment message.

### SlaveService

This service handles communication between slave servers and the master server for receiving updates.

#### RPCs

- `AcceptUpdates`: Accepts updates from the master server.
- `UpdateMaster`: Updates the master server's address and ID.
- `UpdateSlaves`: Updates the slave servers with new data.

#### Messages

- `NewMasterRequest`: Request message for updating the master server.
- `UpdateSlavesRequest`: Request message for updating slave servers.
- `AcceptUpdatesRequest`: Request message for accepting updates from the master server.

## Components

### Master Server

The master server (`master_server.py`) is responsible for managing and coordinating the slave servers. It accepts new slave registrations and sends updates to the slaves as needed. The master server also handles heartbeats from the slaves to monitor their status.

### Slave Server

The slave server (`slave_server.py`) stores a copy of the application's data and processes client requests. It communicates with the master server to receive updates and inform the master of its current status.

### Base Client

The `base_client.py` file contains the BaseClient class, which is a generic implementation of a chat client. This class can be extended to create different types of chat clients, such as a terminal-based client or a GUI-based client.

### Terminal Client

The `terminal_client.py` file extends the BaseClient class to create a terminal-based chat client. This client allows users to interact with the application using a command-line interface.

### GUI Client

The `gui_client.py` file extends the BaseClient class to create a GUI-based chat client. This client provides a graphical interface for users to interact with the application.

### Models

The `models.py` file contains the data models used in the application, such as User and Message. These models are used to store and manage the application's data.

### Utilities

The `utils.py` file contains utility functions used throughout the application, such as functions for hashing passwords and generating session IDs.

## Testing

The `tests/` directory contains unit tests for various components of the application. These tests help ensure that the application's components function as expected.

- `test_base_client.py`: Unit tests for the base_client.py file.
- `test_client.py`: Unit tests for the gui_client.py and terminal_client.py files.
- `test_database.py`: Unit tests for the models.py file.
- `test_server.py`: Unit tests for the master_server.py and slave_server.py files.

To run the tests, execute the following command from the project's root directory:

```
python -m unittest discover tests
```

This command will discover and run all the test files in the `tests/` directory.

## How to Use

To use the chat application, follow these steps:

1. Start the master server by running `master_server.py`:

```
python src/master_server.py
```

2. Start one or more slave servers by running `slave_server.py`:

```
python src/slave_server.py
```

3. Start a client instance, either using the terminal-based client or the GUI-based client:

- For the terminal-based client, run:

```
python src/terminal_client.py
```

- For the GUI-based client, run:

```
python src/gui_client.py
```

4. Interact with the application by creating user accounts, logging in, sending messages, and managing user accounts through the client interface.

## Conclusion

This documentation provides an overview of the N-failstop fault-tolerant chat application, including its file organization, protocol buffer definitions, components, and usage instructions. The application is designed to be resilient against up to N failstop faults and uses a master-slave architecture to ensure fault tolerance. The gRPC protocol is used for communication between the components, and the application supports both terminal-based and GUI-based clients.
