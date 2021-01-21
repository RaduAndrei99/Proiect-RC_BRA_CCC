"""
	Clasa folosita pentru a defini un pachet. 
	Format: Intre 64 si 65535 de octeti
		- primul octet: 0x00 - pachet ce contine de initializare (nume fisier, dimensiune pachete de date, numarul de pachete de date ce urmeaza sa fie transmis)
						0x01 - pachet de initializare
						0x02 - pachet de ACK
						0x03 - pacchet de verificare conexiune
		- urmatorii trei octeti: indexul pachetului (pot fi maxim 16.777.216 de pachete pentru un fisier) - de la 0 la 2^24 - 1
		- in cazul pachetelor de init: * urmatorii 3 octeti contin numarul de pachete de date ce vor fi transmise de catre sender
									   * urmatorii 2 octeti contin dimensiunea pachetelor de date ce urmeaza sa fie transmise	
		- ultimii octeti: 
						 * daca pachetul este de tip initializare, va contine numele fisierului 
						 * daca pachetul este de tip data, va contine date efective
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
			self.__byte_array[10:self.__package_size] = data_array_in_bytes
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
			self.__byte_array[4:7] = no_of_packets.to_bytes(3, byteorder="big")
		else:
			raise "Cannot define the number of packets field for type " + str(self.__byte_array[0])

	def set_packet_size(self, pk_size):
		if self.__byte_array[0] == PacketType.INIT:
			self.__byte_array[7:9] = pk_size.to_bytes(2, byteorder="big")
		else:
			raise "Cannot define the packet size field for type " + str(self.__byte_array[0])
	
	def set_window_size(self, window_size):
		if self.__byte_array[0] == PacketType.INIT:
			self.__byte_array[9:10] = window_size.to_bytes(1, byteorder="big")
		else:
			raise "Cannot define the window size field for type " + str(self.__byte_array[0])

if __name__ == '__main__':
	packet = SWPacket(36,4,4,packet_type=PacketType.ACK)
	print(packet)