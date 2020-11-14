import socket

IP = "127.0.0.1"
PORT = 1234
msg = b"Hello from the other side."

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
s.sendto(msg, (IP, PORT))