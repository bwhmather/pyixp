import socket
import threading
import unittest

from pyixp.marshall import Marshall


class SyncTest(unittest.TestCase):
    def test_echo(self):
        """ check that framing of requests matches un-framing of responses
        """
        client_socket, server_socket = socket.socketpair()

        def echo():
            try:
                while True:
                    data = server_socket.recv(8)
                    server_socket.sendall(data)
            except:
                # we don't care about problems here
                pass

        threading.Thread(target=echo, daemon=True).start()

        marshall = Marshall(client_socket)

        messages = [
            b'asdfghjkl',
        ]

        for message in messages:
            assert marshall.request(message) == message

        marshall.shutdown()
        server_socket.close()
