import socket
import sys

HOST = "127.0.0.1"
PORT = 12345

# Message from Flask (command-line argument)
if len(sys.argv) < 2:
    message = "Default message from client"
else:
    message = sys.argv[1]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.sendall(message.encode())

response = client_socket.recv(1024).decode()
print("CLIENT: Sent ->", message)
print("CLIENT: Received ->", response)

client_socket.close()
