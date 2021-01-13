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

	signal = pyqtSignal(str)

	DATA_PACKET_SIZE = 68
	CHECK_PACKET_SIZE = 4
	ACK_PACKET_SIZE = 4
	LOG_BUFFER_SIZE = 10000

	DATA_SIZE = 64
	PACKET_HEADER_SIZE = 4

	SW_SIZE = 10

	def __init__(self, rcv_ip, rcv_port, probability):
		super(Receiver, self).__init__()

		self.is_running = False

		self.__receiver_ip = rcv_ip
		self.__receiver_port = rcv_port
		self.__losing_packets_probability = probability

		self.SWR = {}
		self.last_packet_received = -1

		self.__file_writer = FileWriter("")
		self.__ups = UnPackingSystem(self.DATA_PACKET_SIZE, self.DATA_SIZE)
		self.__log_buffer = Queue(maxsize=self.LOG_BUFFER_SIZE)

	def create_socket(self, af_type, sock_type):

		check_socket(af_type, sock_type)

		self.__s = socket.socket(af_type_dic.get(af_type), sock_type_dic.get(sock_type)) # IPV4, UDP
		self.__s.bind((self.__receiver_ip, self.__receiver_port))
		self.signal.emit("S-a facut bind pe adresa: " + str(self.__receiver_ip) + " si portul: " + str(self.__receiver_port))

	def check_connection(self):

		self.__s.setblocking(0)
		self.signal.emit("Se asteapta mesaje...")
		check_packet = SWPacket(self.CHECK_PACKET_SIZE, 0, self.PACKET_HEADER_SIZE, packet_type=PacketType.CHECK)

		while self.is_running == False:
			try:
				data_readed, address = self.__s.recvfrom(self.CHECK_PACKET_SIZE)
			except:
				continue

			data_packet.create_packet(data_readed)
			type, data_check, data_null = self.__ups.unpack(data_packet)
			
			if type == PacketType.CHECK:
				self.signal.emit("Am primit mesaj de confirmare al conexiunii de la adresa: " + str(address))
				self.__s.sendto(data_readed, address)

		self.signal.emit("Nu se mai asteapta mesaje...")
		self.__s.setblocking(1)
		

	def start_receiver(self):

		self.signal.emit("A inceput thread-ul de gestionare a pachetelor.")

		data_packet = SWPacket(self.DATA_PACKET_SIZE, self.DATA_SIZE, self.PACKET_HEADER_SIZE, packet_type=PacketType.DATA)
		ack_packet = SWPacket(self.ACK_PACKET_SIZE, 0, self.PACKET_HEADER_SIZE, packet_type=PacketType.ACK)

		name = "new_"

		while self.is_running:

			data_readed, address = self.__s.recvfrom(self.DATA_PACKET_SIZE)

			if is_packet_lost(self.__losing_packets_probability): # Verificam daca vom pierde intentionat acest pachet
				continue

			data_packet.create_packet(data_readed)
			type, nr_packet, data = self.__ups.unpack(data_packet)

			self.signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit pachetul cu numarul: " + str(nr_packet))
			ack_packet.set_packet_number(nr_packet) # Trimitem ACK pentru fiecare pachet primit
			self.__s.sendto(ack_packet.get_header(), address)

			################################################

			if nr_packet == self.last_packet_received + 1: # Mecanism sliding window
				
				if type == PacketType.INIT:
					name += data.decode("ascii")
					start = time.time()
				elif type == PacketType.DATA:
					if self.__file_writer.is_open() == False:
						self.__file_writer.set_file_name(name)
						self.__file_writer.open_file()
						self.__file_writer.write_in_file(data)
					else:
						self.__file_writer.write_in_file(data)
				else:
					self.signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit ultimul pachet.")
					self.last_packet_received += 1
					self.is_running = False
					break
		
				self.last_packet_received += 1

				while self.last_packet_received + 1 in self.SWR.keys():

					(type, data) = self.SWR[self.last_packet_received + 1]
					self.SWR.pop(self.last_packet_received + 1)

					if type == PacketType.INIT:
						name += data
					elif type == PacketType.DATA:
						if self.__file_writer.is_open() == False:
							self.__file_writer.set_file_name(name)
							self.__file_writer.open_file()
							self.__file_writer.write_in_file(data)
						else:
							self.__file_writer.write_in_file(data)
					else:
						self.last_packet_received += 1
						self.signal.emit("[" + str(datetime.now().time()) + "] " + "Am primit ultimul pachet in while-ul interior.")
						self.is_running = False
						break

					self.last_packet_received += 1
					self.signal.emit("[" + str(datetime.now().time()) + "] " + "Sunt in while-ul interior")

			elif nr_packet > self.last_packet_received + 1:
				self.SWR[nr_packet] = (type, data)

			###################################################

			#self.signal.emit("Dimensiunea ferestrei este: " + str(len(self.SWR)))
			#keys = ""
			#for x in self.SWR.keys():
			#	keys += str(x) + " "
			#self.signal.emit(keys)

		self.__file_writer.close_file()
		self.last_packet_received = -1 # Resetam receiver-ul
		end = time.time()
		self.signal.emit("Done!")
		self.signal.emit("Timp de executie: " + str(end - start))
		self.is_running = False

	def set_is_running(self, bool_val):
		self.is_running = bool_val

	def get_socket(self):
		return self.__s

	def close_connection(self):
		self.signal.emit("[" + str(datetime.now().time()) + "] " + "Socket inchis.")
		self.__s.close()

from receiver_window import ReceiverGUI