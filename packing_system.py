from file_reader import FileReader
from packet import SWPacket

"""
	Clasa folosita pentru a impacheta datele dintr-un fisier
"""
class PackingSystem:
	def __init__(self, source_file):
		self.__packet_size_in_bytes = 24
		self.__data_size_in_bytes = 20
		self.__file_reader = FileReader(source_file, self.__data_size_in_bytes)

		self.__first_time = True

		self.__packet_number = 0


	def pack_data(self):
		if self.__first_time:
			self.open_file()
			self.__first_time = False
			self.__packet_number = 0

		new_packet = SWPacket(self.__packet_size_in_bytes, data_packet=True)
		new_packet.set_packet_number(self.__packet_number)
		self.__packet_number += 1
		new_packet.store_data(self.__file_reader.read())
		#print(new_packet.get_data())
		return new_packet.get_data()

	def open_file(self):
		self.__file_reader.open()

	def close_file(self):
		self.__file_reader.close()

if __name__ == '__main__':
	ps = PackingSystem("Receiver.py")
	for i in range(100):
		ps.pack_data()
	ps.close_file()






