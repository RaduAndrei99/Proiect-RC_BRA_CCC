import socket
from packing_system import PackingSystem

IP = "127.0.0.1"
PORT = 1234
msg = b"Hello from the other side."

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP

ps = PackingSystem()
ps.open_file("TestFiles/rufus.exe") # fisier de transmis, momentan hard-coded
print(int(ps.get_file_size()))
for i in range( int(ps.get_file_size() / ps.get_data_size_in_bytes() + 1)):
		print("Am trimis pachetul " + str(i))
		s.sendto(ps.pack_data(), (IP, PORT))
s.sendto(ps.get_end_file_packet(), (IP, PORT))
ps.close_file()
