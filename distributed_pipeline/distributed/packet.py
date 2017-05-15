from abc import ABCMeta, abstractmethod
from enum import Enum
import struct

class PacketType(Enum):
	Packet = 0
	Register = 1
	Load = 2
	
#4 bytes for packet type
#4 bytes for packet size
class Header:
	type = None
	size = 0
	def __init__(self):
		1
	def unpack(self, bytes):
		#Take them all out
		try:
			self.type = struct.unpack_from("i", bytes[0:4])[0]
			self.size = struct.unpack_from("i", bytes[4:8])[0]
		except Exception as e:
			print "Error unpacking " + str(e)

	def pack(self):
		try:
			return struct.pack("i", self.type.value) + struct.pack("i", self.size)
		except Exception as e:
			print "Error packing " + str(e)
			return None


		

class Packet:
	__metaclass__ = ABCMeta

	@abstractmethod
	def unpack(self,bytes):
		pass
	def pack(self,):
		pass

class RegisterPacket(Packet):
	__metaclass = ABCMeta
	id = None
	def __init__(self):
		1
	def unpack(self, bytes):
		try:
			self.id = struct.unpack_from("i", bytes[0:4])[0]
		except Exception as e:
			print "Error unpacking " + str(e)

	def pack(self):
		try:
			return struct.pack("i", self.id)
		except Exception as e:
			print "Error packing " + str(e)

#From directory to peer
class LoadPacket(Packet):
	id = None
	index = None
	def __init__(self):
		1
	def unpack(self, bytes):
		try:
			self.id = struct.unpack_from("q", bytes[0:8])[0]
			self.index = struct.unpack_from("i", bytes[8:12])[0]
		except Exception as e:
			print "Error unpacking " + str(e)
	def pack(self):
		try:
			print struct.pack("q", long(self.id)) + struct.pack("i", int(self.index))
			return struct.pack("q", long(self.id)) + struct.pack("i", int(self.index))
		except Exception as e:
			print "Error packing " + str(e)

