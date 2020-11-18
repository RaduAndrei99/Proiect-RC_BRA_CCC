from file_reader import FileReader
from packet import SWPacket

"""
	Clasa folosita pentru a impacheta datele dintr-un fisier
"""
class PackingSystem:
	def __init__(self):
		self.__packet_size_in_bytes = 24
		self.__data_size_in_bytes = 20

		self.__packet_number = 0


	def pack_data(self):
		new_packet = SWPacket(self.__packet_size_in_bytes, data_packet=True)
		new_packet.set_packet_number(self.__packet_number)
		self.__packet_number += 1
		new_packet.store_data(self.__file_reader.read())
		print(new_packet.get_data())
		return new_packet.get_data()

	def open_file(self, source_file):
		self.__file_reader = FileReader(source_file, self.__data_size_in_bytes)
		self.__file_reader.open()

	def close_file(self):
		self.__file_reader.close()

	def get_file_size(self):
		return self.__file_reader.get_file_size_in_bytes()

	def get_data_size_in_bytes(self):
		return self.__data_size_in_bytes
	
	def get_end_file_packet(self):
		end_packet = SWPacket(self.__packet_size_in_bytes, data_packet=True)

		end_packet.make_end_packet()
		end_packet.set_packet_number(self.__packet_number)


		return end_packet.get_data()






