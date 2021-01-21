import os
import socket
import sys
import time
import random

from file_writer import FileWriter
from unpacking_system import UnPackingSystem
from packet import SWPacket, PacketType
from queue import Queue
from datetime import datetime
from multiprocessing import Process

from PyQt5.QtCore import QObject, QThread, pyqtSignal

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

def is_packet_lost(probability):	# Functia returneaza un rezultat boolean.
	try:							# Probabilitatea stabilita stabileste probabilitatea de a returna False.
		if probability == 0:		# Folosita pentru a se stabili daca se va pierde pachetul primit la nivelul receiver-ului.
			return False
			
		if probability < 0 or probability > 100:
			raise ValueError("Invalid probability! Expect: 0 to 100.")
	except Exception as e:
		print(e)
		sys.exit(1)

	return (random.randint(0, 99) < probability)

'''
	Clasa ce defineste tipul de data Receiver.
	Clasa defineste entitatea care se ocupa cu primrea pachetelor prin intermediul unui socket dat ca membru si gestionate folosind protocolul cu fereastra glisata. 
'''

class Receiver(QObject):

	log_signal = pyqtSignal(str)						# Obiect de tip pyqtSignal menit sa transmita mesaje catre log-ul din interfata grafica.
	finish_signal = pyqtSignal()						# Obiect de tip pyqtSignal menit sa transmita un semnal in momentul in care se termina de primit pachete.
	set_total_nr_of_packets_signal = pyqtSignal(int)	# Obiect de tip pyqtSignal menit sa transmita un semnal in momentul in care se cunoaste numarul total de pachete ce urmeaza sa se primeasca.
	loading_bar_signal = pyqtSignal(int)				# Obiect de tip pyqtSignal menit sa transmita un semnal in care se primeste un pachet.

	INIT_PACKET_SIZE = 64								# Dimensiunea pachetului de initializare. Este stabilita ca fiind 64 de octeti.
	DATA_PACKET_SIZE = INIT_PACKET_SIZE					# Dimensiunea pachetului de date. Initial nu se cunoaste dimensiunea pachetului ce va fi transmis. Se intializeaza cu 64 octeti.
	CHECK_PACKET_SIZE = 4								# Dimensiunea pachetului de confirmare
	ACK_PACKET_SIZE = 4									# Dimensiunea pachetului de acknowledge

	PACKET_TYPE_SIZE = 1								# Dimensiunea campului tipului de pachet primit
	PACKET_COUNTER_SIZE = 3								# Dimensiunea campului numarului de secventa din pachet
	DATA_SIZE = DATA_PACKET_SIZE - PACKET_COUNTER_SIZE - PACKET_TYPE_SIZE	# Dimensiunea campului de date din pachete de date
	PACKET_HEADER_SIZE = PACKET_TYPE_SIZE + PACKET_COUNTER_SIZE				# Dimensiunea header-ului pachetului

	FIRST_PACKET = 0

	def __init__(self):
		super(Receiver, self).__init__()

		socket.setdefaulttimeout(10)					# Setarea timeout-ului de asteptare al socket-ului la 10 secunde

		self.__error_occurred = False					# Variabila booleana care specifica daca s-a intamplat vreo eroare inainte de inceperea primrii pachetelor
		self.__is_socket_open = False					# Variabila booleana care specifica daca socket-ul este deschis.

		self.__receiver_ip = None						# IP-ul receiver-ului.
		self.__receiver_port = None						# Portul receiver-ului
		self.__losing_packets_probability = 0			# Probabilitatea de pierdere a pachetelor

		self.__is_running = True						# Variabila booleana care specifica daca receiver-ul ruleaza
		self.__SWR = {}									# Fereastra protocolului sliding window de la nivelul receiver-ului
		self.__SWR_size = -1							# Dimensiunea ferestrei
		self.__last_packet_received = -1				# Ultimul pachet primit
		self.__total_nr_of_packets_to_receive = -1		# Numarul total de pachete care se vor primi

		self.__file_writer = FileWriter("")					# Obiect de tip FileWriter care gestioneaza fisierul in care se vor scrie datele primite.
		self.__ups = UnPackingSystem(self.DATA_PACKET_SIZE)	# Obiect de tip UnPackingSystem care desparte datele primite in campuri de biti.

		self.__nr_of_packets_recv = 0						# Numarul total de pachete primite
		self.__nr_of_packets_lost = 0						# Numarul total de pachete pierdute

	'''
		Functie membru pentru crearea unui socket
	'''
	def create_socket(self, af_type, sock_type):

		random.seed(datetime.now())
		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

		try:
			self.__s.bind((self.__receiver_ip, self.__receiver_port))
			self.__is_socket_open = True
		except OSError as os:
			self.log_signal.emit("Nu se poate face bind pe adresa precizata. Adresa indisponibila.")
			self.__error_occurred = True
			return

		self.log_signal.emit("S-a facut bind pe adresa: " + str(self.__receiver_ip) + " si portul: " + str(self.__receiver_port))

	'''
		Functie membru pentru reinitializarea membrilor receiver-ului dupa terminarea acestuia
	'''
	def reset_receiver(self):
		self.DATA_PACKET_SIZE = self.INIT_PACKET_SIZE
		self.DATA_SIZE = -1
		self.__is_running = True
		self.__SWR.clear()
		self.__SWR_size = -1
		self.__last_packet_received = -1
		self.__total_nr_of_packets_to_receive = -1
		self.__nr_of_packets_lost = 0
		self.__nr_of_packets_recv = 0

	'''
		Functie membru care implementeaza functionalitatea receiver-ului 
	'''
	def start_receiver(self):

		if self.__error_occurred == True:		# Daca s-a intamplat vreo eroare la crearea socket-ului, procedura de gestionare a pachetelor nu mai are loc. 
			self.__error_occurred = False
			return

		data_packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.INIT)
		ack_packet = SWPacket(self.ACK_PACKET_SIZE, 0, self.PACKET_HEADER_SIZE, packet_type=PacketType.ACK)

		name = "new_"

		self.log_signal.emit("Probabilitatea de pierdere a pachetelor este: " + str(self.__losing_packets_probability))
		self.log_signal.emit("Se asteapta pachete...")

		########################### Incepere gestionare pachete ###############################

		while self.__is_running:

			try:
				data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)		# Primire pachete
			except socket.timeout:
				self.log_signal.emit("Timeout-ul de " + str(socket.getdefaulttimeout()) + " al receiver-ului s-a terminat.")
				self.__is_running = False
				continue
			except OSError as os:
				if "[WinError 10040]" in str(os):
					self.log_signal.emit("[WinError 10040] S-a primit un pachet mai mare decat dimensiunea buffer-ului de receptie.")
					self.log_signal.emit("Se asteapta pachete in continuare...")
					continue

			self.__nr_of_packets_recv += 1

			########################### Testarea conexiunii ###############################

			if int.from_bytes(data_readed[:self.PACKET_HEADER_SIZE - self.PACKET_COUNTER_SIZE], "big") == PacketType.CHECK:	# Retrimitere pachete de conexiune
				self.log_signal.emit("Am primit mesaj de testare a conexiunii de la adresa: " + str(address))
				self.__s.sendto(data_readed, address)
				continue

			########################### Aruncare pachete ###############################

			data_packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(data_packet)

			if is_packet_lost(self.__losing_packets_probability) or (self.__last_packet_received == -1 and nr_packet != self.FIRST_PACKET and nr_packet != 0xFFFFFF): # Verificam daca vom pierde intentionat acest pachet
				self.log_signal.emit("Am aruncat pachetul cu numarul: " + str(nr_packet))
				self.__nr_of_packets_lost += 1
				continue

			########################### Trimitere ACK ###############################

			self.log_signal.emit("Am primit pachetul cu numarul: " + str(nr_packet))
			ack_packet.set_packet_number(nr_packet) # Trimitem ACK pentru fiecare pachet primit

			self.__s.sendto(ack_packet.get_header(), address)

			########################### Mecanism sliding window ###############################

			if nr_packet == self.__last_packet_received + 1:	# Gestionarea pachetului urmator 

				if type == PacketType.DATA:
					if self.__file_writer.is_open() == True:
						self.__file_writer.write_in_file(data)
					else:
						self.log_signal.emit("S-a incercat scrierea intr-un fisier inchis.")

				elif type == PacketType.INIT:
					if nr_packet == self.FIRST_PACKET:
						
						start = time.time()

						self.__total_nr_of_packets_to_receive = int.from_bytes(self.__ups.get_byte_x_to_y(1, 3, data), "big")
						self.set_total_nr_of_packets_signal.emit(self.__total_nr_of_packets_to_receive)
						
						self.DATA_PACKET_SIZE = int.from_bytes(self.__ups.get_byte_x_to_y(4, 5, data), "big")
						self.DATA_SIZE = self.DATA_PACKET_SIZE - self.PACKET_HEADER_SIZE
						
						data_packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.DATA)
						
						self.log_signal.emit("Se vor primii " + str(self.__total_nr_of_packets_to_receive) + " pachete a cate " + str(self.DATA_PACKET_SIZE) + " octeti fiecare.")
						self.__ups.set_packet_size(self.DATA_PACKET_SIZE)

						self.__SWR_size = int.from_bytes(self.__ups.get_byte_x_to_y(6, 6, data), "big")
						self.log_signal.emit("Dimensiunea ferestrei este: " + str(self.__SWR_size))

						name += self.__ups.get_byte_x_to_y(7, self.DATA_SIZE, data).decode("ascii")
						
						self.__file_writer.set_file_name(name)
						self.__file_writer.open_file()
						self.log_signal.emit("Am deschis fisierul cu numele: " + name)

				else:
					self.__last_packet_received += 1
					self.log_signal.emit("Ultimul pachet a fost: " + str(self.__last_packet_received))
					self.loading_bar_signal.emit(nr_packet + 1)
					break
		
				self.__last_packet_received += 1

				while self.__last_packet_received + 1 in self.__SWR.keys():	# Gestionarea pachetului care ocupa primul loc din fereastra 

					(type, data) = self.__SWR[self.__last_packet_received + 1]
					self.__SWR.pop(self.__last_packet_received + 1)

					if type == PacketType.DATA:
						if self.__file_writer.is_open() == True:
							self.__file_writer.write_in_file(data)
						else:
							self.log_signal.emit("S-a incercat scrierea intr-un fisier inchis.")
					else:
						self.__last_packet_received += 1
						self.__is_running = False
						self.log_signal.emit("Ultimul pachet a fost: " + str(self.__last_packet_received))
						break

					self.__last_packet_received += 1

			elif nr_packet > self.__last_packet_received + 1:	# Gestionarea pachetului primit care nu ar ocupa primul loc din fereastra

				if nr_packet == 0xFFFFFF:
					self.__is_running = False
					continue

				self.__SWR[nr_packet] = (type, data)

				if len(self.__SWR) > self.__SWR_size:
					self.log_signal.emit("Eroare! S-a depasit dimensiunea ferestrei. Se opreste receptia pachetelor.")
					self.__is_running = False
					continue

			self.loading_bar_signal.emit(self.__last_packet_received + 1) 	# Update loading bar

			########################### Terminare executie receiver ###############################

		if self.__total_nr_of_packets_to_receive == self.__last_packet_received + 1:
			end = time.time()
			self.log_signal.emit("Done!")
			self.log_signal.emit("Timp de executie: " + str(end - start))
			self.log_signal.emit("Procentul de pachete pierdute este: " + str(100 * float("{:.4f}".format(float(self.__nr_of_packets_lost/self.__nr_of_packets_recv), 2))) + "%")

		else:
			self.log_signal.emit("Program inchis de utilizator sau sender-ul s-a oprit.")

		if self.__file_writer.is_open():			# Inchidem fisier
			self.__file_writer.close_file()
			self.log_signal.emit("Fisierul s-a inchis.")

		while self.__total_nr_of_packets_to_receive == self.__last_packet_received + 1:	# Trimitem ACK-uri pierdute
			
			try:
				data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)
			except socket.timeout:
				self.log_signal.emit("Timeout-ul de " + str(socket.getdefaulttimeout()) + " al receiver-ului in partea de ACK s-a terminat.")
				break

			data_packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(data_packet)

			if nr_packet == 0xFFFFFF:
				self.log_signal.emit("Program finalizat cu succes.")
				break
			elif nr_packet > self.__last_packet_received - self.__SWR_size:	# Verificam ca pachete primite sa ocupe ultima fereastra
				self.log_signal.emit("Am primit ACK pentru pachetul cu numarul: " + str(nr_packet))
				ack_packet.set_packet_number(nr_packet)

				self.__s.sendto(ack_packet.get_header(), address)

		self.close_connection()

		self.finish_signal.emit() # Resetam butoanele interfetei
		self.reset_receiver()

	def set_ip_address(self, ip_address):
		self.__receiver_ip = ip_address

	def set_port(self, port):
		self.__receiver_port = port

	def set_probability(self, probability):
		self.__losing_packets_probability = probability

	def get_ip_address(self):
		return self.__receiver_ip

	def get_port(self):
		return self.__receiver_port

	def set_is_running(self, bool_val):
		self.__is_running = bool_val

	def get_socket(self):
		return self.__s

	def close_connection(self):
		self.log_signal.emit("Socket-ul s-a inchis.")
		self.__is_socket_open = False

		try:
			self.__s.close()
		except AttributeError as ae:
			self.log_signal.emit("Nu se poate inchide un socket ne declarat.")

	def is_socket_open(self):
		return self.__is_socket_open

from receiver_window import ReceiverGUI