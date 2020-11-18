import os
import socket
from FileWriter import FileWriter
from UnPackingSystem import UnPackingSystem
from packet import SWPacket

IP = "127.0.0.1"
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
s.bind((IP, PORT))

# Dimeniunea fisierului va fi pe maxim 24 de octei -> maxim 320 MB
# data[1:24] de la indexul 2 pana in indexul 24

packet = SWPacket(24, True)
fileWriter = FileWriter("out.exe") #fisier primit, momentan cu numele hard-coded
unPackingSystem = UnPackingSystem()

name = ""

while True:
	dataReaded, address = s.recvfrom(24) # Dimensiunea buffer-ului este de 1024 24
										 # Blocheaza thread-ul pana la primirea unui mesaj
	
	print(dataReaded)

	packet.create_packet(dataReaded)
	type, nrPacket, data = unPackingSystem.Unpack(packet)

	if type == 1:
		name += data.decode("ascii")

	elif type == 0:
		if fileWriter.isOpen() == False:
			#fileWriter.setFileName(name)
			fileWriter.openFile()

		if data == b"":
			break

		fileWriter.writeInFile(data)
	else:
		break

fileWriter.closeFile()
s.close()


