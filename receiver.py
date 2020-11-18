import os
import socket
from file_writer import FileWriter
from unpacking_system import UnPackingSystem
from packet import SWPacket

IP = "127.0.0.1"
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
s.bind((IP, PORT))

# Dimeniunea fisierului va fi pe maxim 24 de octei -> maxim 320 MB
# data[1:24] de la indexul 2 pana in indexul 24

packet = SWPacket(24, True)
file_writer = FileWriter("out.exe") #fisier primit, momentan cu numele hard-coded
ups = UnPackingSystem()

name = ""

while True:
	data_readed, address = s.recvfrom(24) # Dimensiunea buffer-ului este de 1024 24
										# Blocheaza thread-ul pana la primirea unui mesaj
	
	print(data_readed)

	packet.create_packet(data_readed)
	type, nr_packet, data = ups.unpack(packet)

	if type == 1:
		name += data.decode("ascii")

	elif type == 0:
		if file_writer.is_open() == False:
			#file_writer.set_file_name(name)
			file_writer.open_file()

		file_writer.write_in_file(data)
	else:
		break

file_writer.close_file()
s.close()


