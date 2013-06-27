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
        self.pack_and_unpack(fields.uint16, 0)
        self.pack_and_unpack(fields.uint16, 0xffff)
        self.pack_and_unpack(fields.uint16, 0xff00)
        self.pack_and_unpack(fields.uint16, 0x0123)

        self.pack_and_unpack(fields.uint32, 0)
        self.pack_and_unpack(fields.uint32, 0xffffffff)
        self.pack_and_unpack(fields.uint32, 0xffff0000)
        self.pack_and_unpack(fields.uint32, 0x01234567)
        self.pack_and_unpack(fields.uint32, 0x89abcdef)

        self.pack_and_unpack(fields.uint64, 0)
        self.pack_and_unpack(fields.uint64, 0xffffffffffffffff)
        self.pack_and_unpack(fields.uint64, 0xffff0000ffff0000)
        self.pack_and_unpack(fields.uint64, 0x0123456789abcded)
        self.pack_and_unpack(fields.uint64, 0x89abcdef01234567)

    def test_data(self):
        data = fields.Data(fields.uint16)
        self.pack_and_unpack(data, b"Hello World")

    def test_string(self):
        string2 = fields.String(fields.uint16)

        self.pack_and_unpack(string2, "Hello World")

    def test_array(self):
        # elements with fixed length
        uint32_array = fields.Array(fields.uint16, fields.uint32)
        self.pack_and_unpack(uint32_array, [])
        self.pack_and_unpack(uint32_array, [1234, 5678, 91011])

        # elements with variable length
        string = fields.String(fields.uint16)
        string_array = fields.Array(fields.uint16, string)
        self.pack_and_unpack(string_array, ["hello", "world", "!"])

    def test_sequence(self):
        seq = fields.Sequence(fields.uint16, fields.String(), fields.uint32)
        self.pack_and_unpack(seq, (5, "test string", 9,))

    def test_struct(self):
        struct = fields.Struct(
            ("foo", fields.uint16,),
            ("bar", fields.String(),),
            ("baz", fields.uint32,))
        self.pack_and_unpack(struct, {"foo": 5, "bar": "test", "baz": 9})
