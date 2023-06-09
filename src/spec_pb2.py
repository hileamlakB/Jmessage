# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spec.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nspec.proto\x1a\x1fgoogle/protobuf/timestamp.proto\":\n\x14\x43reateAccountRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"O\n\x0eServerResponse\x12\x12\n\nerror_code\x18\x01 \x01(\x05\x12\x15\n\rerror_message\x18\x02 \x01(\t\x12\x12\n\nsession_id\x18\x03 \x01(\t\"M\n\"AcknowledgeReceivedMessagesRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\x12\x13\n\x0bmessage_ids\x18\x02 \x03(\x05\"2\n\x0cLoginRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\">\n\x0bSendRequest\x12\n\n\x02to\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x12\n\nsession_id\x18\x03 \x01(\t\"$\n\x0eReceiveRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\"3\n\x0b\x43hatRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\"*\n\x14\x44\x65leteAccountRequest\x12\x12\n\nsession_id\x18\x01 \x01(\t\"m\n\x07Message\x12\r\n\x05\x66rom_\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x12\n\nmessage_id\x18\x03 \x01(\x05\x12.\n\ntime_stamp\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"P\n\x08Messages\x12\x12\n\nerror_code\x18\x01 \x01(\x05\x12\x15\n\rerror_message\x18\x02 \x01(\t\x12\x19\n\x07message\x18\x03 \x03(\x0b\x32\x08.Message\"\x07\n\x05\x45mpty\"(\n\x04User\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t\"\x1c\n\x05Users\x12\x13\n\x04user\x18\x01 \x03(\x0b\x32\x05.User\"E\n\x10NewMasterRequest\x12\x1a\n\x12new_master_address\x18\x01 \x01(\t\x12\x15\n\rnew_master_id\x18\x02 \x01(\t\"*\n\x13UpdateSlavesRequest\x12\x13\n\x0bupdate_data\x18\x01 \x01(\x0c\"?\n\x14RegisterSlaveRequest\x12\x10\n\x08slave_id\x18\x01 \x01(\t\x12\x15\n\rslave_address\x18\x02 \x01(\t\"l\n\x15RegisterSlaveResponse\x12\x12\n\nerror_code\x18\x01 \x01(\x05\x12\x15\n\rerror_message\x18\x02 \x01(\t\x12\x12\n\npickled_db\x18\x03 \x01(\x0c\x12\x14\n\x0cother_slaves\x18\x04 \x03(\t\"+\n\x14\x41\x63\x63\x65ptUpdatesRequest\x12\x13\n\x0bupdate_data\x18\x01 \x01(\x0c\"0\n\x03\x41\x63k\x12\x12\n\nerror_code\x18\x01 \x01(\x05\x12\x15\n\rerror_message\x18\x02 \x01(\t2\xc4\x03\n\rClientAccount\x12\x37\n\rCreateAccount\x12\x15.CreateAccountRequest\x1a\x0f.ServerResponse\x12\x1b\n\tListUsers\x12\x06.Empty\x1a\x06.Users\x12\'\n\x05Login\x12\r.LoginRequest\x1a\x0f.ServerResponse\x12%\n\x04Send\x12\x0c.SendRequest\x1a\x0f.ServerResponse\x12)\n\x0bGetMessages\x12\x0f.ReceiveRequest\x1a\t.Messages\x12\"\n\x07GetChat\x12\x0c.ChatRequest\x1a\t.Messages\x12S\n\x1b\x41\x63knowledgeReceivedMessages\x12#.AcknowledgeReceivedMessagesRequest\x1a\x0f.ServerResponse\x12\x37\n\rDeleteAccount\x12\x15.DeleteAccountRequest\x1a\x0f.ServerResponse\x12\x30\n\x06Logout\x12\x15.DeleteAccountRequest\x1a\x0f.ServerResponse2\x87\x01\n\rMasterService\x12>\n\rRegisterSlave\x12\x15.RegisterSlaveRequest\x1a\x16.RegisterSlaveResponse\x12\x19\n\tHeartBeat\x12\x06.Empty\x1a\x04.Ack\x12\x1b\n\x0b\x43heckMaster\x12\x06.Empty\x1a\x04.Ack2\x9c\x01\n\x0cSlaveService\x12\x37\n\rAcceptUpdates\x12\x15.AcceptUpdatesRequest\x1a\x0f.ServerResponse\x12\'\n\x0cUpdateMaster\x12\x11.NewMasterRequest\x1a\x04.Ack\x12*\n\x0cUpdateSlaves\x12\x14.UpdateSlavesRequest\x1a\x04.Ackb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'spec_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CREATEACCOUNTREQUEST._serialized_start=47
  _CREATEACCOUNTREQUEST._serialized_end=105
  _SERVERRESPONSE._serialized_start=107
  _SERVERRESPONSE._serialized_end=186
  _ACKNOWLEDGERECEIVEDMESSAGESREQUEST._serialized_start=188
  _ACKNOWLEDGERECEIVEDMESSAGESREQUEST._serialized_end=265
  _LOGINREQUEST._serialized_start=267
  _LOGINREQUEST._serialized_end=317
  _SENDREQUEST._serialized_start=319
  _SENDREQUEST._serialized_end=381
  _RECEIVEREQUEST._serialized_start=383
  _RECEIVEREQUEST._serialized_end=419
  _CHATREQUEST._serialized_start=421
  _CHATREQUEST._serialized_end=472
  _DELETEACCOUNTREQUEST._serialized_start=474
  _DELETEACCOUNTREQUEST._serialized_end=516
  _MESSAGE._serialized_start=518
  _MESSAGE._serialized_end=627
  _MESSAGES._serialized_start=629
  _MESSAGES._serialized_end=709
  _EMPTY._serialized_start=711
  _EMPTY._serialized_end=718
  _USER._serialized_start=720
  _USER._serialized_end=760
  _USERS._serialized_start=762
  _USERS._serialized_end=790
  _NEWMASTERREQUEST._serialized_start=792
  _NEWMASTERREQUEST._serialized_end=861
  _UPDATESLAVESREQUEST._serialized_start=863
  _UPDATESLAVESREQUEST._serialized_end=905
  _REGISTERSLAVEREQUEST._serialized_start=907
  _REGISTERSLAVEREQUEST._serialized_end=970
  _REGISTERSLAVERESPONSE._serialized_start=972
  _REGISTERSLAVERESPONSE._serialized_end=1080
  _ACCEPTUPDATESREQUEST._serialized_start=1082
  _ACCEPTUPDATESREQUEST._serialized_end=1125
  _ACK._serialized_start=1127
  _ACK._serialized_end=1175
  _CLIENTACCOUNT._serialized_start=1178
  _CLIENTACCOUNT._serialized_end=1630
  _MASTERSERVICE._serialized_start=1633
  _MASTERSERVICE._serialized_end=1768
  _SLAVESERVICE._serialized_start=1771
  _SLAVESERVICE._serialized_end=1927
# @@protoc_insertion_point(module_scope)
