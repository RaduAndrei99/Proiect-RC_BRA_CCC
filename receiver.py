import os
import socket
import sys
import threading
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

	DATA_PACKET_SIZE = 68
	CHECK_PACKET_SIZE = 4
	ACK_PACKET_SIZE = 4

	DATA_SIZE = 64
	PACKET_HEADER_SIZE = 4

	FIRST_PACKET = 0

	def __init__(self):
		super(Receiver, self).__init__()

		self.__receiver_ip = 0
		self.__receiver_port = 0
		self.__losing_packets_probability = 0

		self.__is_running = True
		self.__SWR = {}
		self.__last_packet_received = -1
		self.__total_nr_of_packets_to_receive = 0

		self.__file_writer = FileWriter("")
		self.__ups = UnPackingSystem(self.DATA_PACKET_SIZE, self.DATA_SIZE)

	def create_socket(self, af_type, sock_type):

		check_socket(af_type, sock_type)
		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP

		try:
			self.__s.bind((self.__receiver_ip, self.__receiver_port))
		except:
			self.__s.close()
			self.__s.bind((self.__receiver_ip, self.__receiver_port))

		self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "S-a facut bind pe adresa: " + str(self.__receiver_ip) + " si portul: " + str(self.__receiver_port))

	def start_receiver(self):

		data_packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.DATA)
		ack_packet = SWPacket(self.ACK_PACKET_SIZE, 0, self.PACKET_HEADER_SIZE, packet_type=PacketType.ACK)

		name = "new_"

		self.__is_running = True
		self.__SWR.clear()
		self.__last_packet_received = -1
		self.__total_nr_of_packets_to_receive = 0

		self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Se asteapta mesaje...")
		while self.__is_running:

			data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)

			if int.from_bytes(data_readed[:1], "big") == PacketType.CHECK:	# Retrimitere pachete de conexiune
				self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit mesaj de confirmare al conexiunii de la adresa: " + str(address))
				self.__s.sendto(data_readed, address)
				continue


			if is_packet_lost(self.__losing_packets_probability): # Verificam daca vom pierde intentionat acest pachet
				continue

			data_packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(data_packet)

			self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit pachetul cu numarul: " + str(nr_packet))
			ack_packet.set_packet_number(nr_packet) # Trimitem ACK pentru fiecare pachet primit
			self.__s.sendto(ack_packet.get_header(), address)

			################################################

			if nr_packet == self.__last_packet_received + 1: # Mecanism sliding window
				
				if type == PacketType.DATA:
					if self.__file_writer.is_open() == False:
						self.__file_writer.set_file_name(name)
						self.__file_writer.open_file()
						self.__file_writer.write_in_file(data)
					else:
						self.__file_writer.write_in_file(data)
				elif type == PacketType.INIT:
					if nr_packet == self.FIRST_PACKET:
						self.__total_nr_of_packets_to_receive = self.__ups.get_first_n_bytes_from_data_to_int(self.PACKET_HEADER_SIZE - 1, data)
						print("Numarul total de pachete este: " + str(self.__total_nr_of_packets_to_receive))
						self.set_total_nr_of_packets_signal.emit(self.__total_nr_of_packets_to_receive)
						name += self.__ups.get_last_n_bytes_from_data(self.DATA_SIZE - self.PACKET_HEADER_SIZE - 1, data).decode("ascii")
						start = time.time()
					else:
						name += data.decode("ascii")

					continue
				else:
					self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit ultimul pachet.")
					self.__last_packet_received += 1
					self.__is_running = False
					break
		
				self.__last_packet_received += 1

				while self.__last_packet_received + 1 in self.__SWR.keys():

					(type, data) = self.__SWR[self.__last_packet_received + 1]
					self.__SWR.pop(self.__last_packet_received + 1)

					if type == PacketType.DATA:
						if self.__file_writer.is_open() == False:
							self.__file_writer.set_file_name(name)
							self.__file_writer.open_file()
							self.__file_writer.write_in_file(data)
						else:
							self.__file_writer.write_in_file(data)
					elif type == PacketType.INIT:
						if nr_packet == FIRST_PACKET:
							self.__total_nr_of_packets_to_receive = self.__ups.get_first_n_bytes_from_data_to_int(self.PACKET_HEADER_SIZE - 1, data)
							self.set_total_nr_of_packets_signal.emit(self.__total_nr_of_packets_to_receive)
							name += self.__ups.get_last_n_bytes_from_data(self.DATA_SIZE - self.PACKET_HEADER_SIZE - 1, data).decode("ascii")
							start = time.time()
						else:
							name += data.decode("ascii")
					else:
						self.__last_packet_received += 1
						self.signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit ultimul pachet in while-ul interior.")
						self.__is_running = False
						break

					self.__last_packet_received += 1
					self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Sunt in while-ul interior")

			elif nr_packet > self.__last_packet_received + 1:
				self.__SWR[nr_packet] = (type, data)

			self.loading_bar_signal.emit(nr_packet) # Update loading bar

			###################################################

		if self.__file_writer.is_open():
			self.__file_writer.close_file()
			end = time.time()
			self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Done!")
			self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Timp de executie: " + str(end - start))
		else:
			self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Program inchis de utilizator.")

		self.finish_signal.emit()
		self.close_connection()

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
		self.log_signal.emit("[" + str(datetime.now().time()) + "] " + "Socket inchis.")
		self.__s.close()

from receiver_window import ReceiverGUI