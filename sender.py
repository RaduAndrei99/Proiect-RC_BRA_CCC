import socket
import sys
from packing_system import PackingSystem
from packet import SWPacket, PacketType
import time
import threading
from unpacking_system import UnPackingSystem
from queue import Queue
from threading import Condition, Lock
import os
from datetime import datetime 
from PyQt5.QtCore import QObject, QThread, pyqtSignal

import binascii

os.system('cls')


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

class Sender(QObject):
	DEFAULT_IP = "127.0.0.1"
	DEFAULT_PORT = 1235

	DEFAULT_RECEIVER_IP = "127.0.0.1"
	DEFAULT_RECEIVER_PORT = 1234

	DEFAULT_PACKET_DATA_SIZE = 64
	DEFAULT_PACKET_HEADER_SIZE = 4 

	log_message_signal = pyqtSignal(str)

	file_sent_signal = pyqtSignal(bool)

	def __init__(self, snd_ip, snd_port):
		super(Sender, self).__init__()
		self.__sender_ip = snd_ip #ip-ul sender-ului
		self.__sender_port = snd_port #port-ul sender-ului

		self.__receiver_ip = Sender.DEFAULT_RECEIVER_IP
		self.__receiver_port  = Sender.DEFAULT_RECEIVER_PORT #port-ul sender-ului

		self.__timeout_value = 0.2 #valoarea de timeout in secunde cat se asteapta confirmarea pentru primirea unui packet

		self.__ps = PackingSystem() #obiectul pentru impachetarea fisierelor
		self.__ups = UnPackingSystem(4, 0) #obiechtul pentru despachetare

		self.__window_size = 100 #lungimea ferestrei
		self.__next_lowest_package = 1 #valoarea pana la urmatorul cel mai mic pachet din fereastra

		self.__current_packet_number = 0 #pachetul curent care este trimis

		self.__packages_sent_and_received = 0 #numarul de pachete trimise si validate la un moment dat
		self.__lowest_window_package = 0 #pachetul cu numarul de ordine cel mai mic din fereastra curenta

		self.__packet_size = Sender.DEFAULT_PACKET_DATA_SIZE + Sender.DEFAULT_PACKET_HEADER_SIZE #lungimea pachetului 
		self.__packet_data_size = Sender.DEFAULT_PACKET_DATA_SIZE #lungimea datelor dintr-un pachet
		self.__packet_header_size = 4 #lungimea header-ului din pachet

		self.__recent_packets_sent = {} #un dictionar folosit pentru a stoca pachetele recent trimise pentru a le avea la "indemana" in cazul in care trebuie sa fie retransmise
		self.__recent_ACK_received = {} #un dictionar folosit pentru a stoca pachetele de ACK care au venit dupa cel mai mic pachet asteptat

		self.__file_send = False #variabila ce indica daca un fisier s-a trimis sau nu

		self.__QUEUE_SIZE = 10000 #lungimea buffer-ului de trimitere

		self.__buffer = Queue(maxsize = self.__QUEUE_SIZE) #buffer-ul de trimitere

		self.__condition = Condition() #numarul de pachete care au fost puse in buffer

		self.__mutex = Lock()

		self.__valid = False
		
		self.__sender_run_flag = True

		self.__path = "music.mp3"

		self.__MAX_FILE_NAME_SIZE = 64

		self.__resend_val = 20

	def create_socket(self, af_type, sock_type):
		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

		self.__s.bind((self.__sender_ip, self.__sender_port))
		self.log_message_signal.emit("S-a facut bind pe adresa " + self.__sender_ip + " si portul " + str(self.__sender_port))

	def start_sender(self):
		self.__sender_run_flag = True

		thread_1 = threading.Thread(target=self.wait_for_ACK)
		thread_2 = threading.Thread(target=self.send_packages_to_buffer)
		thread_3 = threading.Thread(target=self.send_files_with_SW)

		thread_1.start()
		thread_2.start()
		thread_3.start()

		thread_1.join()
		thread_2.join()
		thread_3.join()

		self.file_sent_signal.emit(True)
		
	def wait_for_ACK(self):
		packet = SWPacket(4,0,4,packet_type=PacketType.ACK)
		last_packet_acknowledged = False
		self.__valid == False
		while 1:
			try:
				data_readed, address = self.__s.recvfrom(4)
				packet.create_packet(data_readed)
				package_type, nr_packet, data = self.__ups.unpack(packet)

				if package_type == PacketType.ACK and nr_packet >= self.__lowest_window_package:

					self.__mutex.acquire()
					try:
						self.__recent_packets_sent.pop(nr_packet)
					except KeyError:
						continue
					finally:
						self.__mutex.release()
						
					self.__packages_sent_and_received += 1
					
					self.log_message_signal.emit("[" + str(datetime.now().time()) + "]"  + " Am primit raspuns pozitiv pentru " + str(nr_packet))	

					if nr_packet == int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 2 or last_packet_acknowledged == True:
						last_packet_acknowledged = True
						if bool(self.__recent_packets_sent) == False:
							self.__valid = True
							break
					
					if nr_packet == self.__lowest_window_package:
						for i in range(self.__lowest_window_package + 1, self.__lowest_window_package + self.__window_size + 1):
							if i not in self.__recent_ACK_received:
								for k in range(self.__lowest_window_package + 1, i):
									self.__recent_ACK_received.pop(k)
								self.__lowest_window_package = i
								break
					else:
						self.__recent_ACK_received[nr_packet] = nr_packet
			except ConnectionResetError as e:
				self.__sender_run_flag = False
				self.log_message_signal.emit("[" + str(datetime.now().time()) + "]"  + " Conexiunea s-a inchis dintr-o cauza necunoscuta.")
				self.log_message_signal.emit("[" + str(datetime.now().time()) + "]"  + " " + str(e))
				self.__recent_packets_sent.clear()
				self.__recent_ACK_received.clear()
				with self.__buffer.mutex:
					self.__buffer.queue.clear()
				self.__s.close()

				return

	
		self.log_message_signal.emit("[" + str(datetime.now().time()) + "]"  + " S-a terminat thread-ul care asteapta mesaje de ACK.")


	def send_packages_to_buffer(self):	
		self.log_message_signal.emit("Se trimite fisierul " + self.__path.split("/")[-1])

		count = 0
		self.__ps.reset()
		self.__ps.open_file(self.__path) 

		first_packet = SWPacket(self.__packet_size, self.__packet_data_size, self.__packet_header_size, packet_type=PacketType.INIT)

		file_name = self.__path.split("/")[-1]

		if len(file_name) > self.__MAX_FILE_NAME_SIZE:
			file_name = file_name[0:self.__packet_data_size-len(file_name.split(".")[-1])] + file_name.split(".")[-1]

		first_packet.store_data(bytes(file_name, 'utf-8'))
		first_packet.make_first_packet()

		packets_to_send = 0

		if self.__ps.get_file_size() % self.__ps.get_data_size_in_bytes() != 0:
			packets_to_send = int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 3
		else:
			packets_to_send = int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 2

		first_packet.set_packets_to_send(packets_to_send.to_bytes(3, byteorder="big"))

		count += 1

		self.__buffer.put(first_packet)

		for i in range( int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 1):
			if self.__sender_run_flag == True:
				self.__condition.acquire()
				if self.__buffer.qsize() == self.__QUEUE_SIZE:
					self.__condition.wait()
				count+=1
				self.__buffer.put(self.__ps.pack_data())
				self.__condition.notify()
				self.__condition.release()
			else:
				self.log_message_signal.emit("S-a terminat thread-ul care pune pachete in buffer mai devreme din cauza unei erori.")
				return


		self.__buffer.put(self.__ps.get_end_file_packet())

		count += 1

		self.log_message_signal.emit("Numarul teoretic de pachete generate: " + str(int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 3))
		self.log_message_signal.emit("Numarul de pachete puse in buffer este: " + str(count))

		self.__packages_sent_to_buffer = count

		self.__ps.close_file()
		self.log_message_signal.emit("S-a terminat thread-ul care pune pachete un buffer.")

	def packet_timeout(self, packet_number, resend_value):
		if resend_value < self.__resend_val:
			if packet_number in self.__recent_packets_sent:
				try:
					self.log_message_signal.emit("Retrimit pachetul " + str(packet_number))		
					self.__s.sendto(self.__recent_packets_sent[packet_number], (self.__receiver_ip, self.__receiver_port))
					resend_value += 1
					threading.Timer(self.__timeout_value, self.packet_timeout, args = [packet_number, resend_value]).start()
				except KeyError:
					return
		else:
			self.log_message_signal.emit("Pachetul " + str(packet_number) + " a fost retrimis de prea multe ori.")
			self.log_message_signal.emit("Se anuleaza transmiterea fisierului.")
			self.__sender_run_flag = False
			self.__recent_packets_sent.clear()
			self.__recent_ACK_received.clear()
			with self.__buffer.mutex:
				self.__buffer.queue.clear()
			self.__s.close()

			return

	def send_files_with_SW(self):
		try:
			self.__packages_sent_and_received = 0
			self.__current_packet_number = 0
			self.__lowest_window_package = 0

			while self.__current_packet_number < int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 3:
				if self.__sender_run_flag == True:
					if self.__current_packet_number >= self.__lowest_window_package and self.__current_packet_number <= self.__lowest_window_package + self.__window_size:
						self.__condition.acquire()
						if self.__buffer.qsize() == 0:
							self.__condition.wait()
						packet_to_send = self.__buffer.get()
						self.__condition.notify()
						self.__condition.release()	

						self.__mutex.acquire()
						try:
							self.__recent_packets_sent[packet_to_send.get_packet_number()] = packet_to_send.get_data()
						finally:
							self.__mutex.release()
							
						self.__current_packet_number += 1

						self.__s.sendto(packet_to_send.get_data(), (self.__receiver_ip, self.__receiver_port))
						self.log_message_signal.emit("Trimit pachetul " + str(packet_to_send.get_packet_number()))		
						threading.Timer(self.__timeout_value, self.packet_timeout, args = [packet_to_send.get_packet_number(), 0]).start()
				else:
					self.log_message_signal.emit("S-a terminat thread-ul care trimite fisiere mai devreme din cauza unei erori.")
					return

			while self.__valid == False:
				if self.__valid == True:
						self.__s.close()
			self.log_message_signal.emit("S-a terminat thread-ul care trimite fisiere.")
			
		except Exception as e:
			self.__sender_run_flag = False
			self.log_message_signal.emit("Conexiunea s-a inchis dintr-o cauza necunoscuta.")
			self.log_message_signal.emit(str(e))
			self.__recent_packets_sent.clear()
			self.__recent_ACK_received.clear()
			with self.__buffer.mutex:
				self.__buffer.queue.clear()
			self.__s.close()

			return

	
	def set_receiver_ip(self, ip):
		self.__receiver_ip = ip
	
	def set_receiver_port(self, port):
		self.__receiver_port = port

	def set_timeout(self, timeout):
		self.__timeout_value = timeout

	def set_window_size(self, window_size):
		self.__window_size = window_size
	
	def set_file_path(self, path):
		self.__path = path
	
	def check_connection(self):
		try:
			self.create_socket("AF_INET", "SOCK_DGRAM")

			self.__s.setblocking(False)
			self.__s.settimeout(5.0)

			test_packet = SWPacket(4, 0, 4, packet_type=PacketType.CHECK)

			print(self.__receiver_ip + " " + str(self.__receiver_port))
			self.__s.sendto(test_packet.get_data(), (self.__receiver_ip, self.__receiver_port))
			data_readed, address = self.__s.recvfrom(4)

			if data_readed != None and int.from_bytes(data_readed[:1], "big") == PacketType.CHECK:
				self.log_message_signal.emit("Conexiunea este valida!")
			else:
				self.log_message_signal.emit("Conexiunea este invalida!")
		except ConnectionResetError:
			self.log_message_signal.emit("Eroare! Conexiunea este invalida!")
		except Exception as e:
			self.log_message_signal.emit(str(e))
	
	def get_receiver_ip(self):
		return self.__receiver_ip

	def get_receiver_port(self):
		return self.__receiver_port

	def set_packet_data_size(self, new_size):
		self.__packet_data_size = new_size
		self.__packet_size = new_size + Sender.DEFAULT_PACKET_HEADER_SIZE

	def set_local_ip_address(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		IP = 0
		try:
			s.connect(('10.255.255.255', 1))
			IP = s.getsockname()[0]
		except:
			IP = '127.0.0.1' 
		self.__sender_ip = IP

from sender_window import Ui_MainWindow
