import socket


def tcp(bindTo="localhost"):
    return _common(socket.SOCK_STREAM, bindTo)


def udp(bindTo="localhost"):
    return _common(socket.SOCK_DGRAM, bindTo)


def _common(socketType, bindTo):
    sock = socket.socket(socket.AF_INET, socketType)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((bindTo, 0))
        return sock.getsockname()[1]
    finally:
        sock.close()
