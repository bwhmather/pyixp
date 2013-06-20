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


class UInt(Field):
    def __init__(self, size, signed=True):
        super(UInt, self).__init__()
        self.size = size

    def pack(self, val):
        assert val == val & 2**(8*self.size) - 1, "Arithmetic overflow"
        return bytes((val >> 8*i) & 0xff for i in range(0, self.size))

    def unpack(self, data, offset=0):
        res = sum((data[offset + i] << 8*i for i in range(0, self.size)))
        return res, self.size

    def repr(self):
        return '%s(%d)' % (self.__class__.__name__, self.size)


class Data(Field):
    def __init__(self, size=2):
        super(Data, self).__init__()
        self._header = UInt(size)

    def pack(self, val):
        return self._header.pack(len(val)) + val

    def unpack(self, data, offset=0):
        body_size, header_size = self._header.unpack(data, offset)
        offset += header_size
        assert offset + body_size <= len(data), "String too long to unpack"
        return data[offset:offset + body_size], header_size + body_size


class String(Data):
    def pack(self, val):
        val = val.encode('utf-8')
        return super(String, self).pack(val)

    def unpack(self, data, offset=0):
        value, size = super(String, self).unpack(data, offset)
        return value.decode('utf-8'), size


class Array(Field):
    def __init__(self, size, item_type):
        super(Array, self).__init__()
        self._header = UInt(size)
        self._item = item_type

    def pack(self, values):
        result = self._header.pack(len(values))
        for value in values:
            result += self._item.pack(value)
        return result

    def unpack(self, data, offset=0):
        start = offset
        item_count, size = self._header.unpack(data, offset)
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
