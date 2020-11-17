
# Clasa permite despachetarea unui pachet primit

class UnPackingSystem:

	def __init__(self):
		pass

	def Unpack(self, packet):

		type = int.from_bytes(packet.data[:1], "big")
		nrPacket = int.from_bytes(packet.data[1:4], "big")
		data = packet.data[4:24]

		return (type, nrPacket, data)

