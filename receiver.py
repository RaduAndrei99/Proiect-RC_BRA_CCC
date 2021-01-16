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

def is_packet_lost(probability):
	try:
		if probability == 0:
			return False
			
		if probability < 0 or probability > 100:
			raise ValueError("Invalid probability! Expect: 0 to 100.")
	except Exception as e:
		print(e)
		sys.exit(1)

	return (random.randint(0, 99) < probability)

class Receiver(QObject):

	log_signal = pyqtSignal(str)
	finish_signal = pyqtSignal()
	set_total_nr_of_packets_signal = pyqtSignal(int)
	loading_bar_signal = pyqtSignal(int)

	INIT_PACKET_SIZE = 64
	DATA_PACKET_SIZE = INIT_PACKET_SIZE
	CHECK_PACKET_SIZE = 4
	ACK_PACKET_SIZE = 4

	PACKET_TYPE_SIZE = 1
	PACKET_COUNTER_SIZE = 3
	DATA_SIZE = DATA_PACKET_SIZE - PACKET_COUNTER_SIZE - PACKET_TYPE_SIZE
	PACKET_HEADER_SIZE = PACKET_TYPE_SIZE + PACKET_COUNTER_SIZE

	FIRST_PACKET = 0

	def __init__(self):
		super(Receiver, self).__init__()

		self.__error_occurred = False
		self.__is_socket_open = False

		self.__receiver_ip = 0
		self.__receiver_port = 0
		self.__losing_packets_probability = 0

		self.__is_running = True
		self.__SWR = {}
		self.__last_packet_received = -1
		self.__total_nr_of_packets_to_receive = -1

		self.__file_writer = FileWriter("")
		self.__ups = UnPackingSystem(self.DATA_PACKET_SIZE, self.DATA_SIZE)

		self.__nr_of_packets_recv = 0
		self.__nr_of_packets_lost = 0

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

	def reset_receiver(self):
		self.DATA_PACKET_SIZE = self.INIT_PACKET_SIZE
		self.DATA_SIZE = -1
		self.__is_running = True
		self.__SWR.clear()
		self.__last_packet_received = -1
		self.__total_nr_of_packets_to_receive = -1
		self.__nr_of_packets_lost = 0
		self.__nr_of_packets_recv = 0

	def start_receiver(self):

		if self.__error_occurred == True:
			self.__error_occurred = False
			return

		data_packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.INIT)
		ack_packet = SWPacket(self.ACK_PACKET_SIZE, 0, self.PACKET_HEADER_SIZE, packet_type=PacketType.ACK)

		name = "new_"

		self.log_signal.emit("Probabilitatea de pierdere a pachetelor este: " + str(self.__losing_packets_probability))
		self.log_signal.emit("Se asteapta pachete...")

		while self.__is_running:

			try:
				data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)		# Primire pachete
			except OSError as os:
				if "[WinError 10040]" in str(os):
					self.log_signal.emit("[WinError 10040] S-a primit un pachet mai mare decat dimensiunea buffer-ul de receptie.")
					self.log_signal.emit("Se asteapta pachete...")
				continue

			self.__nr_of_packets_recv += 1

			########################### Testare a conexiunie ###############################

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
				self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Am aruncat pachetul cu numarul: " + str(nr_packet))
				continue

			########################### Trimitere ACK ###############################

			self.log_signal.emit("Am primit pachetul cu numarul: " + str(nr_packet))
			ack_packet.set_packet_number(nr_packet) # Trimitem ACK pentru fiecare pachet primit

			self.__s.sendto(ack_packet.get_header(), address)

			########################### Mecanism sliding window ###############################

			if nr_packet == self.__last_packet_received + 1:
				
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

						name += self.__ups.get_byte_x_to_y(6, self.DATA_SIZE, data).decode("ascii")
						self.__file_writer.set_file_name(name)
						self.__file_writer.open_file()
						self.log_signal.emit("Am deschis fisierul cu numele: " + name)

				else:
					self.__last_packet_received += 1
					self.log_signal.emit("Ultimul pachet a fost: " + str(self.__last_packet_received))
					self.loading_bar_signal.emit(nr_packet + 1)
					break
		
				self.__last_packet_received += 1

				while self.__last_packet_received + 1 in self.__SWR.keys():

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

			elif nr_packet > self.__last_packet_received + 1:
				self.__SWR[nr_packet] = (type, data)

			self.loading_bar_signal.emit(self.__last_packet_received + 1) # Update loading bar

			###################################################

		if self.__total_nr_of_packets_to_receive == self.__last_packet_received + 1:
			end = time.time()
			self.log_signal.emit("Done!")
			self.log_signal.emit("Timp de executie: " + str(end - start))
			self.log_signal.emit("Procentul de pachete pierdute este: " + str(100 * float("{:.4f}".format(float(self.__nr_of_packets_lost/self.__nr_of_packets_recv), 2))) + "%")

		else:
			self.log_signal.emit("Program inchis de utilizator.")

		if self.__file_writer.is_open():			# Inchidem fisier
			self.__file_writer.close_file()
			self.log_signal.emit("Fisierul s-a inchis.")

		if self.__total_nr_of_packets_to_receive == self.__last_packet_received + 1:	# Trmitem ACK-uri pierdute
			
			data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)

			data_packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(data_packet)

			if nr_packet == 0xFFFFFF:
				self.log_signal.emit("Program inchis de utilizator.")
			else:
				self.log_signal.emit("Am primit ACK pentru pachetul cu numarul: " + str(nr_packet))
				ack_packet.set_packet_number(nr_packet) # Trimitem ACK pentru fiecare pachet primit

				self.__s.sendto(ack_packet.get_header(), address)

		self.close_connection()

		self.finish_signal.emit()				# Resetam buton
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