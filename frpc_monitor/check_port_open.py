import socket

def is_port_open(HOST, PORT:int, TIMEOUT=10):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    result = sock.connect_ex((HOST, PORT))

    sock.close()

    return result == 0
