from collections import namedtuple

from pyixp import fields

word8 = uint8 = fields.UInt(1)
word16 = uint16 = fields.UInt(2)
word32 = uint32 = fields.UInt(4)

string = fields.String(2)

qid = object()
stat = object()


class Message(object):
    def pack(self):
        return self._layout.pack(self)

    @classmethod
    def unpack(cls, data):
        sequence, consumed = cls._layout.unpack(data)
        if len(data) != consumed:
            raise Exception("invalid length")
        return cls._make(sequence)


def message_type(name, type_id, *fields_defs):
    names = (field[0] for field in fields_defs)
    types = (field[1] for field in fields_defs)

    TupleBase = namedtuple(name, names)
    layout = fields.Sequence(*types)

    return type(name, (Message, TupleBase,), {
        "_layout": layout,
        "type_id": type_id})


TVersion = message_type(
    "TVersion", 100,
    ("msize", uint32),
    ("version", string)
)

RVersion = message_type(
    "RVersion", 101,
    ("msize", uint32),
    ("version", string)
)


TAuth = message_type(
    "TAuth", 102,
    ("afid", word32),
    ("uname", string),
    ("aname", string)
)

RAuth = message_type(
    "RAuth", 103,
    ("aqid", fields.Array(2, string))  # TODO
)


TAttach = message_type(
    "TAttach", 104,
    ("fid", word32),
    ("afid", word32),
    ("uname", string),
    ("aname", string)
)

RAttach = message_type(
    "RAttach", 105,
    ("qid", fields.Array(2, string))  # TODO
)


RError = message_type(
    "RError", 107,
    ("ename", string)
)


TFlush = message_type(
    "TFlush", 108,
    ("oldtag", word16)
)

RFlush = message_type(
    "RFlush", 109
)


TWalk = message_type(
    "TWalk", 110,
    ("fid", word32),
    ("newfid", word32),
    ("path", fields.Array(2, string))
)

RWalk = message_type(
    "RWalk", 111,
    ("qid", fields.Array(2, qid))
)


TOpen = message_type(
    "TOpen", 112,
    ("fid", word32),
    ("mode", word8)
)

ROpen = message_type(
    "ROpen", 113,
    ("qid", qid),
    ("iounit", word32)
)


TCreate = message_type(
    "TCreate", 114,
    ("fid", word32),
    ("name", string),
    ("perm", word32),
    ("mode", word8)
)

RCreate = message_type(
    "RCreate", 115,
    ("qid", qid),
    ("iounit", word32)
)


TRead = message_type(
    "TRead", 116,
    ("fid", word32),
    ("offset", fields.UInt(8)),
    ("count", uint32)
)

RRead = message_type(
    "RRead", 117,
    ("data", fields.Data(4))
)


TWrite = message_type(
    "TWrite", 118,
    ("fid", word32),
    ("offset", fields.UInt(8)),
    ("data", fields.Data(4))
)

RWrite = message_type(
    "RWrite", 119,
    ("count", uint32)
)


TClunk = message_type(
    "TClunk", 120,
    ("fid", word32),
)

RClunk = message_type(
    "RClunk", 121
)


TRemove = message_type(
    "TRemove", 122,
    ("fid", word32),
)

TRemove = message_type(
    "TRemove", 122
)


TStat = message_type(
    "TStat", 124,
    ("fid", word32),
)

RStat = message_type(
    "RStat", 125,
    ("stat", stat)
)


TWStat = message_type(
    "TWStat", 126,
    ("fid", word32),
    ("stat", stat)
)

RWStat = message_type(
    "RWStat", 127
)


TOpenFD = message_type(
    "TOpenFD", 98,
    ("fid", word32),
    ("mode", word8)
)

ROpenFD = message_type(
    "ROpenFD", 99,
    ("qid", qid),
    ("iounit", word32),
    ("unixfd", word32)
)
