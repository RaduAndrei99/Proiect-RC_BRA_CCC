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

'''
	Clasa ce defineste entitatea care se ocupa cu transmiterea pachetelor prin intermediul protocolului cu fereastra glisanta
	Mosteneste QOBject pentru a se putea implementa semnalele menite sa comunice cu thread-ul care ruleaza interfata grafica
	in scopul transmiterii de mesaje
'''
class Sender(QObject):
	DEFAULT_IP = "127.0.0.1" #IP-ul default
	DEFAULT_PORT = 1235 #port-ul default

	DEFAULT_RECEIVER_IP = "127.0.0.1" #IP-ul default al receiverului
	DEFAULT_RECEIVER_PORT = 1234 #port-ul default al receiverului

	DEFAULT_PACKET_DATA_SIZE = 64 # dimensiunea default a campului de date dintr-un pachet 
	DEFAULT_PACKET_HEADER_SIZE = 4 #dimensiunea header-ului

	log_message_signal = pyqtSignal(str) #obiect de tip pyqtSignal pentru a transmite mesaje catre log-ul din interfata grafica

	file_sent_signal = pyqtSignal(bool) #semnal pentru a transmite finalizarea transmiterii fisierului

	def __init__(self, snd_ip, snd_port):
		super(Sender, self).__init__()
		self.__sender_ip = snd_ip #ip-ul sender-ului
		self.__sender_port = snd_port #port-ul sender-ului

		self.__receiver_ip = Sender.DEFAULT_RECEIVER_IP
		self.__receiver_port  = Sender.DEFAULT_RECEIVER_PORT #port-ul sender-ului

		self.__timeout_value = 0.2 #valoarea de timeout in secunde cat se asteapta confirmarea pentru primirea unui packet

		self.__ps = PackingSystem() #obiectul pentru impachetarea fisierelor
		self.__ups = UnPackingSystem(4) #obiechtul pentru despachetare

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

		self.__mutex = Lock() #mutex folosit pentru a asigura coerenta datelor pentru dicitonarul care retine pachetele care asteapta mesaje de ACK

		self.__valid = False  #boolean folosit pentru a sincroniza terminarea functiilor de wait_for_ack si send_files_with_SW
		
		self.__sender_run_flag = False #flag-ul de run

		self.__path = "" #path-ul catre fisierul care urmeaza sa fie trimis

		self.__MAX_FILE_NAME_SIZE = 54 #dimensiunea maxima de caractere pe care poate sa il aiba un fisier ( + extensie)

		self.__resend_val = 20 #indica de cate ori se retrimite un pachet pana cand se decide sa se anuleze transmisiunea

	def create_socket(self, af_type, sock_type):
		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

		self.__s.bind((self.__sender_ip, self.__sender_port))
		self.log_message_signal.emit("S-a facut bind pe adresa " + self.__sender_ip + " si portul " + str(self.__sender_port))

	def start_sender(self):
		self.__sender_run_flag = True
		self.__recent_packets_sent.clear()
		self.__recent_ACK_received.clear()
		self.__buffer.queue.clear()

		#thread_1 = threading.Thread(target=self.wait_for_ACK)
		#thread_2 = threading.Thread(target=self.send_packages_to_buffer)
		#thread_3 = threading.Thread(target=self.send_files_with_SW)

		self.send_packages_to_buffer()
		
		#thread_1.start()
		#thread_2.start()
		#thread_3.start()

		#thread_1.join()
		#thread_2.join()
		#thread_3.join()

		self.file_sent_signal.emit(True)
		self.__sender_run_flag = False
		self.log_message_signal.emit("S-a terminat thread-ul sender-ului")	


	def wait_for_ACK(self):
		try:
			self.log_message_signal.emit("S-a pornit thread-ul care asteapta mesaje de ACK")	
			packet = SWPacket(4,0,4,packet_type=PacketType.ACK)
			last_packet_acknowledged = False
			self.__valid == False
			while 1:
				if self.__sender_run_flag == True:
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
						
						self.log_message_signal.emit("Am primit raspuns pozitiv pentru " + str(nr_packet))	

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
				else:
					break
				
		except Exception as e:
			self.__sender_run_flag = False
			self.log_message_signal.emit("wait_for_ack: Conexiunea s-a inchis dintr-o cauza necunoscuta.")
			self.log_message_signal.emit(str(e))
			self.__recent_packets_sent.clear()
			self.__recent_ACK_received.clear()
			self.__s.close()
			return


		self.log_message_signal.emit("S-a terminat thread-ul care asteapta mesaje de ACK.")


	def send_packages_to_buffer(self):	
		try:
			self.log_message_signal.emit("Se trimite fisierul " + self.__path.split("/")[-1])

			count = 0
			self.__ps.reset()
			self.__ps.open_file(self.__path) 

			if self.__ps.get_file_size() < (2**24 - 2)*self.__packet_size:

				first_packet = SWPacket(self.__packet_size, self.__packet_data_size, self.__packet_header_size, packet_type=PacketType.INIT)

				file_name = self.__path.split("/")[-1]

				if len(file_name) > self.__MAX_FILE_NAME_SIZE:
					file_name = file_name[0:self.__MAX_FILE_NAME_SIZE-len(file_name.split(".")[-1])-1] + "."  + file_name.split(".")[-1]
					print(file_name)


				first_packet.store_data(bytes(file_name, 'utf-8'))

				packets_to_send = 0

				if self.__ps.get_file_size() % self.__ps.get_data_size_in_bytes() != 0:
					packets_to_send = int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 3
				else:
					packets_to_send = int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 2

				first_packet.set_packets_to_send(packets_to_send)
				first_packet.set_window_size(self.__window_size)

				count += 1

				first_packet.set_packet_size(self.__packet_size)

				self.__buffer.put(first_packet)

				thread_1 = threading.Thread(target=self.wait_for_ACK)
				thread_2 = threading.Thread(target=self.send_files_with_SW)

				thread_1.start()
				thread_2.start()

				print(binascii.hexlify(first_packet.get_data()))
				for i in range( int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 1):
					if self.__sender_run_flag == True:
						self.__condition.acquire()
						if self.__buffer.qsize() == self.__QUEUE_SIZE:
							self.__condition.wait(timeout=2)
							if self.__sender_run_flag == False:
								self.__condition.notify()
								self.__condition.release()	
								continue
						self.__buffer.put(self.__ps.pack_data())
						self.__condition.notify()
						self.__condition.release()
						count+=1
					else:
						self.__ps.close_file()
						self.log_message_signal.emit("S-a terminat thread-ul care pune pachete in buffer mai devreme din cauza unei erori.")

						thread_1.join()
						thread_2.join()						
						return


				self.__buffer.put(self.__ps.get_end_file_packet())

				count += 1

				self.log_message_signal.emit("Numarul teoretic de pachete generate: " + str(int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 3))
				self.log_message_signal.emit("Numarul de pachete puse in buffer este: " + str(count))

				self.__ps.close_file()
				self.log_message_signal.emit("S-a terminat thread-ul care pune pachete un buffer.")

				thread_1.join()
				thread_2.join()
			else:
				self.log_message_signal.emit("Fisierul este prea mare pentru a putea fi trimis!")
				self.log_message_signal.emit("Va rugam mariti dimensiunea campului de date din pachet daca se poate.")
		except Exception as e:
			self.__sender_run_flag = False
			self.log_message_signal.emit("send_packages_to_buffer: Conexiunea s-a inchis dintr-o cauza necunoscuta.")
			self.log_message_signal.emit(str(e))
			self.__recent_packets_sent.clear()
			self.__recent_ACK_received.clear()
			self.__s.close()
			return


	def packet_timeout(self, packet_number, resend_value):
		if resend_value < self.__resend_val:
			if packet_number in self.__recent_packets_sent:
				try:
					self.log_message_signal.emit("Retrimit pachetul " + str(packet_number))		
					self.__s.sendto(self.__recent_packets_sent[packet_number], (self.__receiver_ip, self.__receiver_port))
					resend_value += 1
					threading.Timer(self.__timeout_value, self.packet_timeout, args = [packet_number, resend_value]).start()
				except Exception as e:
					self.log_message_signal.emit(str(e))		
		else:
			self.log_message_signal.emit("Pachetul " + str(packet_number) + " a fost retrimis de prea multe ori.")
			self.log_message_signal.emit("Se anuleaza transmiterea fisierului.")
			self.__sender_run_flag = False
			self.__recent_packets_sent.clear()
			self.__recent_ACK_received.clear()
			self.__s.close()

			return

	def send_files_with_SW(self):
		try:
			self.log_message_signal.emit("S-a pornit thread-ul care trimite pachetele")	

			self.__packages_sent_and_received = 0
			self.__current_packet_number = 0
			self.__lowest_window_package = 0

			while self.__current_packet_number < int(self.__ps.get_file_size() / self.__ps.get_data_size_in_bytes()) + 3:
				if self.__sender_run_flag == True:
					if self.__current_packet_number >= self.__lowest_window_package and self.__current_packet_number < self.__lowest_window_package + self.__window_size:
						self.__condition.acquire()
						if self.__buffer.qsize() == 0:
							self.__condition.wait(timeout=2)
							if self.__sender_run_flag == False:
								self.__condition.notify()
								self.__condition.release()	
								continue
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
			self.__s.settimeout(10)

			test_packet = SWPacket(4, 0, 4, packet_type=PacketType.CHECK)

			self.__s.sendto(test_packet.get_data(), (self.__receiver_ip, self.__receiver_port))
			data_readed, address = self.__s.recvfrom(4)

			if data_readed != None and int.from_bytes(data_readed[:1], "big") == PacketType.CHECK:
				self.log_message_signal.emit("Conexiunea este valida!")
			else:
				self.log_message_signal.emit("Conexiunea este invalida!")

			self.__s.close()
		except ConnectionResetError:
			self.log_message_signal.emit("Eroare! Conexiunea este invalida!")
		except Exception as e:
			self.log_message_signal.emit(str(e))
		finally:
			self.__s.close()

	def get_receiver_ip(self):
		return self.__receiver_ip

	def get_receiver_port(self):
		return self.__receiver_port

	def set_packet_data_size(self, new_size):
		self.__packet_data_size = new_size
		self.__packet_size = new_size + Sender.DEFAULT_PACKET_HEADER_SIZE
		self.__ps.set_data_size(new_size)

	def set_local_ip_address(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		IP = 0
		try:
			s.connect(('10.255.255.255', 1))
			IP = s.getsockname()[0]
		except:
			IP = '127.0.0.1' 
		self.__sender_ip = IP

	def set_loopback_ip_address(self):
		self.__sender_ip = "127.0.0.1"
	
	def is_running(self):
		return self.__sender_run_flag
	
	def close_sender(self):
		if self.__sender_run_flag == True:
			data_packet = SWPacket(self.__packet_size, self.__packet_data_size, self.__packet_header_size, packet_type=PacketType.DATA)
			data_packet.make_end_packet()
			data_packet.set_packet_number(0xFFFFFF)

			self.__s.sendto(data_packet.get_data(), (self.__receiver_ip, self.__receiver_port))
			self.__sender_run_flag = False

			self.__s.close()

from sender_window import SenderGUI