
# Clasa permite despachetarea unui pachet primit

class UnPackingSystem:
	def __init__(self, packet_size_in_bytes, data_size_in_bytes):
		self.__packet_size_in_bytes = packet_size_in_bytes
		self.__data_size_in_bytes = data_size_in_bytes

		self.__packet_number = 0

	def unpack(self, packet):
		type = int.from_bytes(packet.get_data()[:1], "big")
		nr_packet = int.from_bytes(packet.get_data()[1:4], "big")
		data = packet.get_data()[4:self.__packet_size_in_bytes]

		return (type, nr_packet, data)

	def get_first_n_bytes_from_data_to_int(self, n, data):
		return int.from_bytes(data[:n], "big")

	def get_last_n_bytes_from_data(self, n, data):
		return data[3:]
