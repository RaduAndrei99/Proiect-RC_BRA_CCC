import socket
import sys
from packing_system import PackingSystem
from packet import SWPacket, PacketType
from time import sleep 
import threading
from unpacking_system import UnPackingSystem

IP = "127.0.0.1"
PORT = 1234

packet_size = 36
packet_data_size = 32
packet_header_size = 4

count = 0

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

class Sender:

	def __init__(self, snd_ip, snd_port):
		self.__sender_ip = snd_ip
		self.__sender_port = snd_port

		self.__ps = PackingSystem()
		self.__ups = UnPackingSystem(4, 0)


		self.__window_size = 10

		self.__packet_size = 36
		self.__packet_data_size = 32
		self.__packet_header_size = 4

		self.__recent_packets_sent = {}

	def create_socket(self, af_type, sock_type):
		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

		self.__s.bind((self.__sender_ip, self.__sender_port))


	def start_sender(self):
		thread_1 = threading.Thread(target=self.wait_for_ACK)
		thread_2 = threading.Thread(target=self.send_packets)
		thread_1.start()
		thread_2.start()
		thread_1.join()
		thread_2.join()
	def wait_for_ACK(self):
		packet = SWPacket(4,0,4,packet_type=PacketType.ACK)
		while 1:
			data_readed, address = self.__s.recvfrom(4)
			packet.create_packet(data_readed)

			packet_type, nr_packet = self.__ups.unpack(packet)
			print("Am primit raspuns pozitiv pentru: " + str(nr_packet))

	def send_packets(self):	
		count = 0

		current_sent_packets = 0
		self.__ps.open_file("send.zip") # fisier de transmis, momentan hard-coded

		first_packet = SWPacket(packet_size, packet_data_size, packet_header_size, packet_type=PacketType.INIT)
		first_packet.store_data(b'send.zip')
		print(first_packet.get_data())
		count += 1
		self.__s.sendto(first_packet.get_data(), (IP, PORT) )
		for i in range( int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes() + 1)):
			if current_sent_packets < self.__window_size: 
				ret = self.__ps.pack_data()
				count+=1
				current_sent_packets+=1
				self.__recent_packets_sent[self.__ps.get_current_packet_number()] = ret
				self.__s.sendto(ret, (IP, PORT) )
			else:
				pass
				#astept sa se faca move la fereastra


		self.__s.sendto(self.__ps.get_end_file_packet(), (IP, PORT))
		count += 1

		print("Numarul de pachete este: " + str(count))

		self.__ps.close_file()
		self.__s.close()


if __name__ == '__main__':
	sender = Sender("127.0.0.1", 1235)
	sender.create_socket("AF_INET", "SOCK_DGRAM")
	sender.start_sender()