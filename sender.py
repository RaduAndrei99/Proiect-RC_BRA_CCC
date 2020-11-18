import socket
from packing_system import PackingSystem
from packet import SWPacket

IP = "127.0.0.1"
PORT = 1234

packet_size = 36
packet_data_size = 32
packet_header_size = 4


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP

ps = PackingSystem()
ps.open_file("dell.exe") # fisier de transmis, momentan hard-coded

first_packet = SWPacket(packet_size, packet_data_size, packet_header_size, False)
first_packet.store_data(b'dell.exe')
print(first_packet.get_data())
s.sendto(first_packet.get_data(), (IP, PORT) )
for i in range( int(ps.get_file_size() / ps.get_data_size_in_bytes() + 1)):
		#print("Am trimis pachetul " + str(i))
		ret = ps.pack_data()
		#print(len(ret))
		s.sendto(ret, (IP, PORT) )

s.sendto(ps.get_end_file_packet(), (IP, PORT))
ps.close_file()
