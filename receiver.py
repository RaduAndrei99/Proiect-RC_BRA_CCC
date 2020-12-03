import os
import socket
import sys
from file_writer import FileWriter
from unpacking_system import UnPackingSystem
from packet import SWPacket, PacketType

af_type_dic = {
        	"AF_INET": socket.AF_INET,
        	"AF_INET6":socket.AF_INET6,
}

sock_type_dic = {
        "SOCK_STREAM": socket.SOCK_STREAM,
        "SOCK_DGRAM": socket.SOCK_DGRAM
}

def check_socket(af_type, sock_type):
	try:
		if af_type != "AF_INET" and af_type != "AF_INET6":
			raise ValueError("Invalid protocol family type!")

		if sock_type != "SOCK_STREAM" and sock_type != "SOCK_DGRAM":
			raise ValueError("Invalid socket type!")

	except:
		sys.exit(1)

class Receiver:

	DATA_PACKET_SIZE = 36
	ACK_PACKET_SIZE = 4

	DATA_SIZE = 32
	PACKET_HEADER_SIZE = 4

	def __init__(self, rcv_ip, rcv_port):
		self.__receiver_ip = rcv_ip
		self.__receiver_port = rcv_port

		self.__file_writer = FileWriter("")
		self.__ups = UnPackingSystem(self.DATA_PACKET_SIZE, self.DATA_SIZE)

	def create_socket(self, af_type, sock_type):

		check_socket(af_type, sock_type)

		self.s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP
		self.s.bind((self.__receiver_ip, self.__receiver_port))

	def start_receiver(self):
		
		packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.DATA)

		name = "new_"

		while True:
			data_readed, address = self.s.recvfrom(self.DATA_PACKET_SIZE)

			packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(packet)

			if type == 0:
				name += data.decode("ascii")

			elif type == 1:
				if self.__file_writer.is_open() == False:
					self.__file_writer.set_file_name(name)
					self.__file_writer.open_file()

				#Threading

				self.__file_writer.write_in_file(data)

			else:
				break

		self.__file_writer.close_file()
		self.s.close()


if __name__ == '__main__':
	receiver = Receiver("127.0.0.1", 1234)
	receiver.create_socket("AF_INET", "SOCK_DGRAM")
	receiver.start_receiver()




