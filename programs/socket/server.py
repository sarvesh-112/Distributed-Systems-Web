import socket

HOST = "127.0.0.1"
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("SERVER: Listening on", HOST, PORT)

conn, addr = server_socket.accept()
print("SERVER: Connected by", addr)

# Receive message from client
client_message = conn.recv(1024).decode()
print("SERVER: Received ->", client_message)

# Server reply (can be dynamic later)
server_reply = "Server received your message successfully!"
conn.sendall(server_reply.encode())

conn.close()
server_socket.close()

print("SERVER: Connection closed")
