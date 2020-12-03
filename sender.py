import socket
import sys
from packing_system import PackingSystem
from packet import SWPacket
from time import sleep 

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



	def create_socket(self, af_type, sock_type):
		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

	def start_sender(self):

		packet_size = 36
		packet_data_size = 32
		packet_header_size = 4

		count = 0

		self.__ps.open_file("send.zip") # fisier de transmis, momentan hard-coded

		first_packet = SWPacket(packet_size, packet_data_size, packet_header_size, False)
		first_packet.store_data(b'send.zip')
		print(first_packet.get_data())
		count += 1
		self.__s.sendto(first_packet.get_data(), (IP, PORT) )
		for i in range( int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes() + 1)):
				#print("Am trimis pachetul " + str(i))
				ret = self.__ps.pack_data()
				#print(len(ret))
				count+=1
				self.__s.sendto(ret, (IP, PORT) )
				sleep(0.001)


		self.__s.sendto(self.__ps.get_end_file_packet(), (IP, PORT))
		count += 1

		print("Numarul de pachete este: " + str(count))

		self.__ps.close_file()
		self.__s.close()


if __name__ == '__main__':
	sender = Sender("127.0.0.1", 1234)
	sender.create_socket("AF_INET", "SOCK_DGRAM")
	sender.start_sender()