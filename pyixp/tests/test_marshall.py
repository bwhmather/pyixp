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
            request_type, request = 1, message
            response_type, response = marshall.request(request_type, request)
            self.assertEqual(request_type, response_type)
            self.assertEqual(request, response)

        marshall.shutdown()
        server_socket.close()
