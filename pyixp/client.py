from pyixp.marshall import Marshall
from pyixp import requests


class Client(object):
    def __init__(self, connection):
        self._marshall = Marshall(connection)

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
