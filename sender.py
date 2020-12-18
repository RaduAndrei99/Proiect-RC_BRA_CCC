import socket
import sys
from packing_system import PackingSystem
from packet import SWPacket, PacketType
import time
import threading
from unpacking_system import UnPackingSystem
from queue import Queue
from threading import Condition, Lock

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
		self.__sender_ip = snd_ip #ip-ul sender-ului
		self.__sender_port = snd_port #port-ul sender-ului

		self.__ps = PackingSystem() #obiectul pentru impachetarea fisierelor
		self.__ups = UnPackingSystem(4, 0) #obiechtul pentru despachetare

		self.__window_size = 10 #lungimea ferestrei

		self.__current_packages = 0 #numarul curent de pachete care asteapta ACK
		self.__packages_sent_and_received = 0 #numarul de pachete trimise si validate la un moment dat
		self.__lowest_window_package = 0 #pachetul cu numarul de ordine cel mai mic din fereastra curenta

		self.__packet_size = 36 #lungimea pachetului 
		self.__packet_data_size = 32 #lungimea datelor dintr-un pachet
		self.__packet_header_size = 4 #lungimea header-ului din pachet

		self.__recent_packets_sent = {} #un dictionar folosit pentru a stoca pachetele recent trimise pentru a le avea la "indemana" in cazul in care trebuie sa fie retransmise
		self.__file_send = False #variabila ce indica daca un fisier s-a trimis sau nu

		self.__QUEUE_SIZE = 1000 #lungimea buffer-ului de trimitere

		self.__buffer = Queue(maxsize = self.__QUEUE_SIZE) #buffer-ul de trimitere

		self.__condition = Condition() #numarul de pachete care au fost puse in buffer

		self.__recent_packets_sent = {}

		self.__mutex = Lock()

		self.__timeout_value = 1000


	def create_socket(self, af_type, sock_type):
		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

		self.__s.bind((self.__sender_ip, self.__sender_port))


	def start_sender(self):
		thread_1 = threading.Thread(target=self.wait_for_ACK)
		thread_2 = threading.Thread(target=self.send_packages_to_buffer)
		thread_3 = threading.Thread(target=self.send_files_with_SW)

		thread_1.start()
		thread_2.start()
		thread_3.start()

		thread_1.join()
		thread_2.join()
		thread_3.join()


	def wait_for_ACK(self):
		packet = SWPacket(4,0,4,packet_type=PacketType.ACK)
		while 1:
			data_readed, address = self.__s.recvfrom(4)
			packet.create_packet(data_readed)
			package_type, nr_packet, data = self.__ups.unpack(packet)

			if package_type == PacketType.ACK and nr_packet >= self.__lowest_window_package:
				self.__mutex.acquire()
				try:
					self.__current_packages -= 1
				finally:
					self.__mutex.release()
					
				self.__packages_sent_and_received += 1

				if nr_packet == self.__lowest_window_package:
					self.__lowest_window_package = self.__lowest_window_package + 1
				

			#package_type, nr_packet, data = self.__ups.unpack(packet)
			#print("Am primit raspuns pozitiv pentru: " + str(nr_packet))

	def send_packages_to_buffer(self):	
		count = 0

		self.__ps.open_file("music.mp3") # fisier de transmis, momentan hard-coded

		first_packet = SWPacket(packet_size, packet_data_size, packet_header_size, packet_type=PacketType.INIT)
		first_packet.store_data(b'music.mp3')
		print(first_packet.get_data())
		count += 1
		self.__buffer.put(first_packet)
		for i in range( int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 1):
			self.__condition.acquire()
			if self.__buffer.qsize() == self.__QUEUE_SIZE:
				self.__condition.wait()
			count+=1
			self.__buffer.put(self.__ps.pack_data())
			self.__condition.notify()
			self.__condition.release()


		self.__buffer.put(self.__ps.get_end_file_packet())

		count += 1

		print("Numarul de pachete puse in buffer este: " + str(count))

		self.__packages_sent_to_buffer = count

		self.__ps.close_file()

	def send_files_with_SW(self):
		self.__packages_sent_and_received = 0
		while self.__packages_sent_and_received < int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes() + 1) + 2:
			if self.__current_packages <= self.__window_size:
				self.__condition.acquire()
				if self.__buffer.qsize() == 0:
					self.__condition.wait()
				packet_to_send = self.__buffer.get()
				self.__s.sendto(packet_to_send.get_data(), (IP, PORT))
				print("Trimit " + str(packet_to_send.get_packet_number()))
				self.__condition.notify()
				self.__condition.release()

				self.__mutex.acquire()
				try:
					self.__current_packages += 1
				finally:
					self.__mutex.release()


		self.__s.close()

			

if __name__ == '__main__':
	sender = Sender("127.0.0.1", 1235)
	sender.create_socket("AF_INET", "SOCK_DGRAM")
	sender.start_sender()