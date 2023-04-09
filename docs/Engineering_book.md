# Brain Storming

Given that we have a chat app built with gRPC and Python, we want to use SQLite as the database, and here are some options for fault tolerance, along with the tools and requirements for each approach.

1. Raft:

Raft is a consensus algorithm designed for simplicity and understandability. It provides fault tolerance by maintaining a consistent state across a cluster of nodes.

Things we need:

- A Raft library for Python: One option is `pyraft`, which is a minimalistic Raft implementation in Python. Find it here: [https://github.com/soheilpro/pyraft](https://github.com/soheilpro/pyraft)
- A cluster of at least 3 nodes to achieve 2-fault tolerance, with an odd number of nodes being ideal for achieving consensus.

Pros:

- Easier to understand and implement compared to Paxos.
- Provides strong consistency.

Cons:

- Performance overhead due to the consensus algorithm.
- May be more complex than a primary-secondary model for your use case.

2. Paxos:

Paxos is a consensus algorithm that provides fault tolerance by reaching consensus among distributed nodes. It is more complex than Raft but has been widely used in distributed systems.

Things we need:

- A Paxos library for Python: One option is `pypaxos`, a Paxos implementation in Python. Find it here: [https://github.com/ailidani/pypaxos](https://github.com/ailidani/pypaxos)
- A cluster of at least 3 nodes to achieve 2-fault tolerance, with an odd number of nodes being ideal for achieving consensus.

Pros:

- Provides strong consistency.
- Has been widely used and studied in distributed systems.

Cons:

- Complex to understand and implement.
- Performance overhead due to the consensus algorithm.
- May be more complex than a primary-secondary model for your use case.

3. Primary-secondary (master-slave) model:

This model involves a primary node that processes all write requests and secondary nodes that replicate the data from the primary node. In case the primary node fails, one of the secondary nodes can take over as the new primary.

Things you need:

- A replication tool for SQLite, like Litereplica ([https://litereplica.io/](https://litereplica.io/)) or rqlite ([https://github.com/rqlite/rqlite](https://github.com/rqlite/rqlite)).
- At least 3 nodes (1 primary and 2 secondary) to achieve 2-fault tolerance.

Pros:

- Easier to implement compared to Raft and Paxos.
- Lower performance overhead.

Cons:

- Does not provide strong consistency like Raft or Paxos.
- Relies on manual or scripted failover mechanisms in case of primary node failure.

# Decision

We have decided to use the following combinations

1. A chat app with client server model that uses grpc
2. A persistant database with sqlite
3. An ORM with SQL alchemy
4. Fault tolerance with Raft

# Design

# Unittest

# Progress

**`<details><summary>Commit 1: Integrate database</summary>`**

**Database Integration** : We've integrated an SQLite database using SQLAlchemy to store user and message data. We've created two models, `UserModel` and `MessageModel`, for storing user and message information, respectively. Additionally, we've introduced a `DeletedMessageModel` to store deleted messages.

1. **Database Operations** : We've replaced in-memory data structures like `all_users` and `session_map` with database queries and operations. All user and message-related operations now interact with the database, making the application state persistent across server restarts.
2. **Session Management** : We've replaced the server-side session management with a token-based authentication system using session IDs. The session IDs are stored in the user model, allowing for more efficient session management and verification.
3. **Login/Logout** : We've updated the `Login` and `Logout` methods to work with the new session management system and database.
4. **Message Sending and Receiving** : We've updated the `Send`, `GetMessages`, and `AcknowledgeReceivedMessages` methods to work with the database. We've also introduced the concept of acknowledgment for received messages. Messages are now marked as "received" when the client fetches them using `GetMessages`, and they are moved to the `DeletedMessageModel` table upon acknowledgment from the client using the `AcknowledgeReceivedMessages` method. When a user deletes their account, their unreceived messages are also moved to the `DeletedMessageModel` table.
5. **List Users** : We've updated the `ListUsers` method to query the user list from the database instead of the in-memory data structures.
6. **Delete Account** : We've updated the `DeleteAccount` method to remove the user from the database and move unreceived messages to the `DeletedMessageModel` table.
7. **Client-side Changes** : We've updated the client-side code to work with the new server-side changes. The `receive_thread` method now uses `GetMessages` to receive messages and sends an acknowledgment using the `AcknowledgeReceivedMessages` RPC.
8. **Updating gRPC code** : We used the following command to generate updated gRPC code after modifying the `.proto` file:

<pre><div class="bg-black rounded-md mb-4"><div class="flex items-center relative text-gray-200 bg-gray-800 px-4 py-2 text-xs font-sans justify-between rounded-t-md"><span>css</span><button class="flex ml-auto gap-2"><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code</button></div><div class="p-4 overflow-y-auto"><code class="!whitespace-pre hljs language-css">python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./spec.proto
</code></div></div></pre>

This revised chat application provides a more robust, scalable, and persistent solution by using an SQLite database and token-based authentication.


**`</details>`**
