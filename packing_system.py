from file_reader import FileReader
from packet import SWPacket, PacketType

"""
	Clasa folosita pentru a impacheta datele dintr-un fisier
"""
class PackingSystem:
	DEFAULT_PACKET_DATA_SIZE = 4096
	PACKET_HEADER_SIZE = 4
	def __init__(self):
		self.__data_size_in_bytes = PackingSystem.DEFAULT_PACKET_DATA_SIZE
		self.__packet_size_in_bytes = PackingSystem.DEFAULT_PACKET_DATA_SIZE + PackingSystem.PACKET_HEADER_SIZE

		self.__packet_number = 1

		self.__header_size_in_bytes = PackingSystem.PACKET_HEADER_SIZE

	def pack_data(self):
		new_packet = SWPacket(self.__packet_size_in_bytes, self.__data_size_in_bytes, self.__header_size_in_bytes, packet_type=PacketType.DATA)
		new_packet.set_packet_number(self.__packet_number)
		self.__packet_number += 1
		new_packet.store_data(self.__file_reader.read())
		return new_packet

	def open_file(self, source_file):
		self.__file_reader = FileReader(source_file, self.__data_size_in_bytes)
		self.__file_reader.open()

	def close_file(self):
		self.__file_reader.close()

	def get_file_size(self):
		return self.__file_reader.get_file_size_in_bytes()

	def get_current_packet_number(self):
		return self.__packet_number

	def get_data_size_in_bytes(self):
		return self.__data_size_in_bytes
	
	def get_end_file_packet(self):
		end_packet = SWPacket(self.__packet_size_in_bytes, self.__data_size_in_bytes, self.__header_size_in_bytes, packet_type=PacketType.DATA)

		end_packet.make_end_packet()
		end_packet.set_packet_number(self.__packet_number)

		return end_packet

	def reset(self):
		self.__packet_number = 1







