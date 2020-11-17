import socket
from packing_system import PackingSystem

IP = "127.0.0.1"
PORT = 1234
msg = b"Hello from the other side."

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP

ps = PackingSystem("Receiver.py")
for i in range(100):
	s.sendto(ps.pack_data(), (IP, PORT))
ps.close_file()
