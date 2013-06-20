import unittest
import logging
from pyixp import fields


class IdentityTest(unittest.TestCase):
    def pack_and_unpack(self, type_, value):
        packed = type_.pack(value)

        logging.info("packed: %r" % packed)
        self.assertIsInstance(packed, bytes)

        unpacked, size = type_.unpack(packed)

        self.assertEqual(len(packed), size)
        self.assertEqual(value, unpacked)

    def test_uint(self):
        uint32 = fields.UInt(4)
        self.pack_and_unpack(uint32, 0)
        self.pack_and_unpack(uint32, 0xffffffff)
        self.pack_and_unpack(uint32, 0xffff0000)
        self.pack_and_unpack(uint32, 0x01234567)
        self.pack_and_unpack(uint32, 0x89abcdef)

        uint16 = fields.UInt(2)
        self.pack_and_unpack(uint16, 0)
        self.pack_and_unpack(uint16, 0xffff)
        self.pack_and_unpack(uint16, 0xff00)
        self.pack_and_unpack(uint16, 0x0123)

    def test_data(self):
        data = fields.Data(2)
        self.pack_and_unpack(data, b"Hello World")

    def test_string(self):
        string2 = fields.String(2)

        self.pack_and_unpack(string2, "Hello World")

    def test_array(self):
        # elements with fixed length
        uint32 = fields.UInt(4)
        uint32_array = fields.Array(2, uint32)
        self.pack_and_unpack(uint32_array, [])
        self.pack_and_unpack(uint32_array, [1234, 5678, 91011])

        # elements with variable length
        string = fields.String(2)
        string_array = fields.Array(2, string)
        self.pack_and_unpack(string_array, ["hello", "world", "!"])

    def test_sequence(self):
        seq = fields.Sequence(fields.UInt(2), fields.String(2), fields.UInt(4))
        self.pack_and_unpack(seq, (5, "test string", 9,))

    def test_struct(self):
        struct = fields.Struct(
            ("foo", fields.UInt(2),),
            ("bar", fields.String(2),),
            ("baz", fields.UInt(4),))
        self.pack_and_unpack(struct, {"foo": 5, "bar": "test", "baz": 9})
