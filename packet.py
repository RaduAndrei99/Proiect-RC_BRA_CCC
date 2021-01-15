"""
	Clasa folosita pentru a defini un pachet. 
	Format: 68 de octeti
		- primul octet: 0x1 - pachet de initializare
						0x0 - pachet ce contine date

		- urmatorii trei octeti: indexul pachetului (pot fi maxim 16.777.216 de pachete pentru un fisier)
		- ultimii 64 de octeti: 
								daca pachetul este de tip initializare, va contine numele fisierului
								daca pachetul este de tip data, va contine date efective 
"""

import enum

class PacketType(enum.IntEnum):
	INIT = 0
	DATA = 1
	ACK = 2
	CHECK = 3

class SWPacket:
	def __init__(self, pk_size, data_size, header_size, packet_type: PacketType):

		if data_size < pk_size and header_size <= pk_size:
			self.__byte_array = bytearray(pk_size)
			self.__data_size = data_size
			self.__package_size = pk_size
			self.__data_size = data_size
			self.__header_size = header_size
		else:
			pass


		if packet_type == PacketType.INIT:
			self.__byte_array[0] = 0x0
		elif packet_type == PacketType.DATA:
			self.__byte_array[0] = 0x1
		elif packet_type == PacketType.ACK:
			self.__byte_array[0] = 0x2
		elif packet_type == PacketType.CHECK:
			self.__byte_array[0] = 0x3
		
	def get_data(self):
		return self.__byte_array

	def get_packet_number(self):
		return int.from_bytes(self.__byte_array[1:4], "big")

	def get_header(self):
		return self.__byte_array[:self.__header_size]

	def store_data(self, data_array_in_bytes):
		if self.__byte_array[0] == PacketType.DATA:
			self.__byte_array[4:self.__package_size] = data_array_in_bytes
		elif self.__byte_array[0] == PacketType.INIT:
			self.__byte_array[7:self.__package_size] = data_array_in_bytes
		else:
			raise "Cannot set data bytes for a package of type " + str(self.__byte_array[0])

	def set_packet_number(self, pk_number):
		if(pk_number < pow(2, 24)):
			self.__byte_array[1:4] = pk_number.to_bytes(3, byteorder="big")

	def create_packet(self, bytes_array):
		self.__byte_array = bytes_array

	def make_end_packet(self):
		self.__byte_array[0] = 0xFF
	
	def make_first_packet(self):
		self.__byte_array[0] = 0x0
	
	def set_packets_to_send(self, no_of_packets):
		if self.__byte_array[0] == PacketType.INIT:
			self.__byte_array[4:7] = no_of_packets

if __name__ == '__main__':
	packet = SWPacket(36,4,4,packet_type=PacketType.ACK)
	print(packet)