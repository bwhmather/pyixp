from pyixp.marshall import Marshall
from pyixp import requests

import logging

log = logging.getLogger(__name__)

VERSION = "9P2000"


class Client(object):
    def __init__(self, connection, max_message_size=0x0000ffff):
        self._marshall = Marshall(connection)

        resp = self.version(max_message_size, VERSION)
        if resp.msize > max_message_size:
            raise Exception("invalid message size requested by server")
        if resp.version != VERSION:
            raise Exception("unsupported version")
        self._max_message_size = self._marshall.max_message_size = resp.msize

    def version(self, *args, **kwargs):
        return requests.VersionRequest(*args, **kwargs).submit(self._marshall)

    def auth(self, *args, **kwargs):
        return requests.AuthRequest(*args, **kwargs).submit(self._marshall)

    def attach(self, *args, **kwargs):
        return requests.AttachRequest(*args, **kwargs).submit(self._marshall)

    def flush(self, *args, **kwargs):
        return requests.FlushRequest(*args, **kwargs).submit(self._marshall)

    def walk(self, *args, **kwargs):
        return requests.WalkRequest(*args, **kwargs).submit(self._marshall)

    def open(self, *args, **kwargs):
        return requests.OpenRequest(*args, **kwargs).submit(self._marshall)

    def create(self, *args, **kwargs):
        return requests.CreateRequest(*args, **kwargs).submit(self._marshall)

    def read(self, *args, **kwargs):
        return requests.ReadRequest(*args, **kwargs).submit(self._marshall)

    def write(self, *args, **kwargs):
        return requests.WriteRequest(*args, **kwargs).submit(self._marshall)

    def clunk(self, *args, **kwargs):
        return requests.ClunkRequest(*args, **kwargs).submit(self._marshall)

    def remove(self, *args, **kwargs):
        return requests.RemoveRequest(*args, **kwargs).submit(self._marshall)

    def stat(self, *args, **kwargs):
        return requests.StatRequest(*args, **kwargs).submit(self._marshall)

    def wstat(self, *args, **kwargs):
        return requests.WStatRequest(*args, **kwargs).submit(self._marshall)

    def openfd(self, *args, **kwargs):
        return requests.OpenFDRequest(*args, **kwargs).submit(self._marshall)

    def shutdown(self):
        self._marshall.shutdown()

    def close(self):
        self._marshall.close()
