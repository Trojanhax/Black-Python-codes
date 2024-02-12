import socket
import threading

# Define the IP address and port to bind the server socket to
bind_ip = "0.0.0.0"
bind_port = 9998

# Create a socket object using IPv4 and TCP protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to the specified IP address and port
server.bind((bind_ip, bind_port))

# Listen for incoming connections with a maximum backlog of 5
server.listen(5)
print("[*] Listening on %s:%d" % (bind_ip, bind_port))

# Define a function to handle client connections
def handle_client(client_socket):
    # Receive data from the client
    request = client_socket.recv(1024)
    # send packet
    client_socket.send("ACK!")
    print("[*] Received: %s" % request)
    # Close the client socket after receiving data
    client_socket.close()

# Main loop to accept incoming client connections
while True:
    # Accept a client connection and retrieve client socket and address
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
    # Create a new thread to handle the client connection
    client_handler = threading.Thread(target=handle_client, args=(client,))
    # Start the client handler thread
    client_handler.start()
