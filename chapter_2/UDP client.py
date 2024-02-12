import socket

target_host = "127.0.0.1"
target_port = 80

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b"AAABBBCCC", (target_host, target_port))

# receive data
try:
    data, addr = client.recvfrom(4096)
    if data:
        print(data.decode())
    else:
        print("No data received from server.")
except ConnectionResetError as e:
    print("Connection closed by server. Attempting to reconnect.", e)
    # Retry logic or shutdown process
