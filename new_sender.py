cking_system import PackingSystem
from packet import SWPacket, PacketType
import time
import threading
from unpacking_system import UnPackingSystem
from queue import Queue
from threading import Condition, Lock
import os
IP = "127.0.0.1"
PORT = 1234

os.system('cls')

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

		self.__timeout_value = 5 #valoarea de timeout in secunde cat se asteapta confirmarea pentru primirea unui packet

		self.__ps = PackingSystem(