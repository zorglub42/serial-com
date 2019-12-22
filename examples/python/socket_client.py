# coding: utf-8
import socket
import time

hote = "localhost"
port = 9999


def socket_receive(client_socket):
    """Get data from socket.

    socket.recv function overloading
    We are using here the recv exception mecanism to determine if there is
    some data to read

    @param socket Socket to read
    @return Data send by client
    """
    buf = ""  # Buffer to store data
    _has_data = True  # Is there some data to read?
    while _has_data:
        # Use socket as non blocking
        client_socket.setblocking(0)
        try:
            _data = client_socket.recv(256)
            if _data:
                buf += _data.decode()
            else:
                _has_data = False
        except Exception:  # pylint: disable=broad-except
            _has_data = False
    return buf


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((hote, port))
print("Connection on {}".format(port))

socket.send("V\n".encode())
time.sleep(0.500)
data = socket_receive(socket)
while data:
    print("Received: " + data)
    data = socket_receive(socket)

print("Close")
socket.close()
