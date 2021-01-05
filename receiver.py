import os
import socket
import sys
import threading
from time import sleep
import random

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

	except Exception as e:
		print(e)
		sys.exit(1)

def is_packet_lost(probability):
	try:
		if probability < 0 or probability > 100:
			raise ValueError("Invalid probability! Expect: 0 to 100.")
	except Exception as e:
		print(e)
		sys.exit(1)
	
	return (random.randint(0, 99) < probability)

class Receiver:
	LOSING_PACKETS_PROBABILITY = 3 #in procente

	DATA_PACKET_SIZE = 36
	ACK_PACKET_SIZE = 4

	DATA_SIZE = 32
	PACKET_HEADER_SIZE = 4

	SW_SIZE = 10

	def __init__(self, rcv_ip, rcv_port):
		self.__receiver_ip = rcv_ip
		self.__receiver_port = rcv_port

		self.SWR = {}
		self.last_packet_received = -1

		self.__file_writer = FileWriter("")
		self.__ups = UnPackingSystem(self.DATA_PACKET_SIZE, self.DATA_SIZE)

	def create_socket(self, af_type, sock_type):

		check_socket(af_type, sock_type)

		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP
		self.__s.bind((self.__receiver_ip, self.__receiver_port))

	def insert_in_sw(self, nr_packet, data):
		if nr_packet == self.last_packet_received + 1: # Mecanism sliding window
			self.__file_writer.write_in_file(data)
			self.last_packet_received += 1

			while self.last_packet_received + 1 in self.SWR.keys():
				self.__file_writer.write_in_file(self.SWR[self.last_packet_received + 1])
				self.SWR.pop(self.last_packet_received + 1)
				self.last_packet_received += 1
				print ("Sunt in while-ul interior")

		elif nr_packet > self.last_packet_received + 1:
			self.SWR[nr_packet] = data


	def start_receiver(self):
		
		data_packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.DATA)
		ack_packet = SWPacket(self.ACK_PACKET_SIZE, 0, self.PACKET_HEADER_SIZE, packet_type=PacketType.ACK)

		name = "new_"

		while True:
			#print("Astept urmatorul pachet:")
			data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)

			if is_packet_lost(self.LOSING_PACKETS_PROBABILITY): # Verificam daca vom pierde intentionat acest pachet
				continue

			data_packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(data_packet)

			print("Am primit " + str(nr_packet))

			ack_packet.set_packet_number(nr_packet) # Trimitem ACK pentru fiecare pachet primit
			self.__s.sendto(ack_packet.get_header(), address)

			if type == 0:
				self.last_packet_received += 1
				name += data.decode("ascii")

			elif type == 1:
				if self.__file_writer.is_open() == False:
					self.__file_writer.set_file_name(name)
					self.__file_writer.open_file()

				self.insert_in_sw(nr_packet, data)
			else:
				break

			print("Dimensiunea ferestrei este: " + str(len(self.SWR)))
			for x in self.SWR.keys():
				print(x)


		self.__file_writer.close_file()
		self.__s.close()


if __name__ == '__main__':
	receiver = Receiver("127.0.0.1", 1234)
	receiver.create_socket("AF_INET", "SOCK_DGRAM")
	receiver.start_receiver()