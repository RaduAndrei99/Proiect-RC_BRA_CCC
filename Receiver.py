import socket

IP = "127.0.0.1"
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
s.bind((IP, PORT))


for i in range(100):
	data, address = s.recvfrom(1024) #Dimensiunea buffer-ului este de 1024 octeti
										# Blocheaza thread-ul pana la primirea unui mesaj
	print(f'Mesajul primit este {data} de la {address}')