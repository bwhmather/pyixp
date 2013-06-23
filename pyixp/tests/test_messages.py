import unittest

from pyixp.messages import *


class TestMessages(unittest.TestCase):
    def test_t_version(self):
        packed = b"\xff\x00\xff\x00\x05\x001.0.0"

        message_in = TVersion(0xff00ff, "1.0.0")

        self.assertEqual(message_in.pack(), packed)

        message_out = TVersion.unpack(packed)

        self.assertEqual(message_out.msize, 0xff00ff)
        self.assertEqual(message_out.version, "1.0.0")
        self.assertEqual(message_out, message_in)
