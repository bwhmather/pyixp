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


def message_type(name, *fields_):
    names = (field[0] for field in fields_)
    types = (field[1] for field in fields_)

    TupleBase = namedtuple(name, names)
    layout = fields.Sequence(*types)

    return type(name, (Message, TupleBase,), {"_layout": layout})


TVersion = message_type(
    "TVersion",
    ("msize", uint32),
    ("version", string)
)

RVersion = message_type(
    "RVersion",
    ("msize", uint32),
    ("version", string)
)


TAuth = message_type(
    "TAuth",
    ("afid", word32),
    ("uname", string),
    ("aname", string)
)

RAuth = message_type(
    "RAuth",
    ("aqid", fields.Array(2, string))  # TODO
)


RError = message_type(
    "RError",
    ("ename", string)
)


TFlush = message_type(
    "TFlush",
    ("oldtag", word16)
)

RFlush = message_type(
    "RFlush"
)


TAttach = message_type(
    "TAttach",
    ("fid", word32),
    ("afid", word32),
    ("uname", string),
    ("aname", string)
)

RAttach = message_type(
    "RAttach",
    ("qid", fields.Array(2, string))  # TODO
)


TWalk = message_type(
    "TWalk",
    ("fid", word32),
    ("newfid", word32),
    ("path", fields.Array(2, string))
)

RWalk = message_type(
    "RWalk",
    ("qid", fields.Array(2, qid))
)


TOpen = message_type(
    "TOpen",
    ("fid", word32),
    ("mode", word8)
)

ROpen = message_type(
    "ROpen",
    ("qid", qid),
    ("iounit", word32)
)


TOpenFD = message_type(
    "TOpenFD",
    ("fid", word32),
    ("mode", word8)
)

ROpenFD = message_type(
    "ROpenFD",
    ("qid", qid),
    ("iounit", word32),
    ("unixfd", word32)
)


TCreate = message_type(
    "TCreate",
    ("fid", word32),
    ("name", string),
    ("perm", word32),
    ("mode", word8)
)

RCreate = message_type(
    "RCreate",
    ("qid", qid),
    ("iounit", word32)
)


TRead = message_type(
    "TRead",
    ("fid", word32),
    ("offset", fields.UInt(8)),
    ("count", uint32)
)

RRead = message_type(
    "RRead",
    ("data", fields.Data(4))
)


TWrite = message_type(
    "TWrite",
    ("fid", word32),
    ("offset", fields.UInt(8)),
    ("data", fields.Data(4))
)

RWrite = message_type(
    "RWrite",
    ("count", uint32)
)


TClunk = message_type(
    "TClunk",
    ("fid", word32),
)

RClunk = message_type(
    "RClunk"
)


TRemove = message_type(
    "TRemove",
    ("fid", word32),
)

TRemove = message_type(
    "TRemove"
)


TStat = message_type(
    "TStat",
    ("fid", word32),
)

RStat = message_type(
    "RStat",
    ("stat", stat)
)


TWStat = message_type(
    "TWStat",
    ("fid", word32),
    ("stat", stat)
)

RWStat = message_type(
    "RWStat"
)
