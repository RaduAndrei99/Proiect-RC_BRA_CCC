
# Clasa permite despachetarea unui pachet primit

class UnPackingSystem:

	def __init__(self):
		pass

	def unpack(self, packet):

		type = int.from_bytes(packet.get_data()[:1], "big")
		nr_packet = int.from_bytes(packet.get_data()[1:4], "big")
		data = packet.get_data()[4:24]

		return (type, nr_packet, data)

