import struct


class Field(object):
    def pack(self, values):
        """
        :returns: byte array
        """
        raise NotImplementedError()

    def unpack(self, data, offset=0):
        """
        :returns: the decoded value and ammount of data consumed
        """
        raise NotImplementedError()

    def repr(self):
        return self.__class__.__name__

    def __repr__(self):
        if hasattr(self, 'name'):
            return '<Field %s "%s">' % (self.repr(), self.name)
        return super(Field, self).__repr__()


class StructField(Field):
    def __init__(self, format):
        self._struct = struct.Struct(format)

    def pack(self, value):
        return self._struct.pack(value)

    def unpack(self, data, offset=0):
        return self._struct.unpack_from(data, offset)[0], self._struct.size

int8 = StructField("c")
uint8 = StructField("B")

int16 = StructField("h")
int16l = StructField("<h")
uint16 = StructField("H")
uint16l = StructField("<H")

int32 = StructField("i")
int32l = StructField("<i")
uint32 = StructField("I")
uint32l = StructField("<I")

int64 = StructField("q")
int64l = StructField("<q")
uint64 = StructField("Q")
uint64l = StructField("<Q")


class Data(Field):
    def __init__(self, size=uint16):
        super(Data, self).__init__()
        self._size = size

    def pack(self, val):
        if isinstance(self._size, int):
            assert len(val) == self._size
            return val
        else:
            return self._size.pack(len(val)) + val

    def unpack(self, data, offset=0):
        if isinstance(self._size, int):
            body_size = self._size
        else:
            body_size, header_size = self._size.unpack(data, offset)
            offset += header_size
        assert offset + body_size <= len(data), "String too long to unpack"
        return data[offset:offset + body_size], header_size + body_size


class String(Data):
    def __init__(self, size=uint16, encoding='utf-8'):
        super(String, self).__init__(size)
        self._encoding = encoding

    def pack(self, val):
        val = val.encode(self._encoding)
        return super(String, self).pack(val)

    def unpack(self, data, offset=0):
        value, size = super(String, self).unpack(data, offset)
        return value.decode(self._encoding), size


class Array(Field):
    def __init__(self, size, item):
        super(Array, self).__init__()
        self._size = size
        self._item = item

    def pack(self, values):
        result = b''
        if not isinstance(self._size, int):
            result += self._size.pack(len(values))
        for value in values:
            result += self._item.pack(value)
        return result

    def unpack(self, data, offset=0):
        start = offset
        if isinstance(self._size, int):
            item_count = self._size
        else:
            item_count, size = self._size.unpack(data, offset)
            offset += size
        result = []
        for i in range(0, item_count):
            value, size = self._item.unpack(data, offset)
            result.append(value)
            offset += size
        return result, offset - start


class Sequence(Field):
    """ Pack and unpack tuples of elements with different types
    """
    def __init__(self, *fields):
        self._fields = fields

    def pack(self, values):
        return b''.join(field.pack(value)
                        for value, field in zip(values, self._fields))

    def unpack(self, data, offset=0):
        start = offset
        values = []
        for field in self._fields:
            value, size = field.unpack(data, offset)
            values.append(value)
            offset += size
        return tuple(values), offset - start


class Struct(Field):
    """ Field for packing and unpacking dictionaries
    """
    def __init__(self, *fields):
        self._fields = fields

    def pack(self, values):
        return b''.join(type_.pack(values[name])
                        for name, type_ in self._fields)

    def unpack(self, data, offset=0):
        start = offset
        values = {}
        for name, type_ in self._fields:
            value, size = type_.unpack(data, offset)
            values[name] = value
            offset += size

        return values, offset - start
