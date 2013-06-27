from collections import namedtuple

from pyixp import fields


__all__ = [
    "Message",
    "message_type",
    "TVersion", "RVersion",
    "TAuth", "RAuth",
    "TAttach", "RAttach",
    "RError",
    "TFlush", "RFlush",
    "TWalk", "RWalk",
    "TOpen", "ROpen",
    "TCreate", "RCreate",
    "TRead", "RRead",
    "TWrite", "RWrite",
    "TClunk", "RClunk",
    "TRemove", "RRemove",
    "TStat", "RStat",
    "TWStat", "RWStat",
    "TOpenFD", "ROpenFD",
]

timestamp = fields.uint32l
string = fields.String(fields.uint16l)


qid = fields.Struct(
    ("type", fields.uint8),
    ("version", fields.uint32l),
    ("path", fields.uint64l))

stat = fields.Struct(
    ("size", fields.uint16l),
    ("type", fields.uint16l),
    ("dev", fields.uint32l),
    ("qid", qid),
    ("mode", fields.uint32l),
    ("atime", timestamp),
    ("mtime", timestamp),
    ("length", fields.uint64l),
    ("name", string),
    ("uid", string),
    ("gid", string),
    ("muid", string))


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
        "type_id": type_id,
    })


TVersion = message_type(
    "TVersion", 100,
    ("msize", fields.uint32l),
    ("version", string)
)

RVersion = message_type(
    "RVersion", 101,
    ("msize", fields.uint32l),
    ("version", string)
)


TAuth = message_type(
    "TAuth", 102,
    ("afid", fields.uint32l),
    ("uname", string),
    ("aname", string)
)

RAuth = message_type(
    "RAuth", 103,
    ("aqid", fields.Array(fields.uint16l, string))  # TODO
)


TAttach = message_type(
    "TAttach", 104,
    ("fid", fields.uint32l),
    ("afid", fields.uint32l),
    ("uname", string),
    ("aname", string)
)

RAttach = message_type(
    "RAttach", 105,
    ("qid", fields.Array(fields.uint16l, string))  # TODO
)


RError = message_type(
    "RError", 107,
    ("ename", string)
)


TFlush = message_type(
    "TFlush", 108,
    ("oldtag", fields.uint16l)
)

RFlush = message_type(
    "RFlush", 109
)


TWalk = message_type(
    "TWalk", 110,
    ("fid", fields.uint32l),
    ("newfid", fields.uint32l),
    ("path", fields.Array(fields.uint16l, string))
)

RWalk = message_type(
    "RWalk", 111,
    ("qid", fields.Array(fields.uint16l, qid))
)


TOpen = message_type(
    "TOpen", 112,
    ("fid", fields.uint32l),
    ("mode", fields.uint8)
)

ROpen = message_type(
    "ROpen", 113,
    ("qid", qid),
    ("iounit", fields.uint32l)
)


TCreate = message_type(
    "TCreate", 114,
    ("fid", fields.uint32l),
    ("name", string),
    ("perm", fields.uint32l),
    ("mode", fields.uint8)
)

RCreate = message_type(
    "RCreate", 115,
    ("qid", qid),
    ("iounit", fields.uint32l)
)


TRead = message_type(
    "TRead", 116,
    ("fid", fields.uint32l),
    ("offset", fields.uint64l),
    ("count", fields.uint32l)
)

RRead = message_type(
    "RRead", 117,
    ("data", fields.Data(fields.uint32l))
)


TWrite = message_type(
    "TWrite", 118,
    ("fid", fields.uint32l),
    ("offset", fields.uint64l),
    ("data", fields.Data(fields.uint32l))
)

RWrite = message_type(
    "RWrite", 119,
    ("count", fields.uint32l)
)


TClunk = message_type(
    "TClunk", 120,
    ("fid", fields.uint32l),
)

RClunk = message_type(
    "RClunk", 121
)


TRemove = message_type(
    "TRemove", 122,
    ("fid", fields.uint32l),
)

RRemove = message_type(
    "RRemove", 122
)


TStat = message_type(
    "TStat", 124,
    ("fid", fields.uint32l),
)

RStat = message_type(
    "RStat", 125,
    ("stat", stat)
)


TWStat = message_type(
    "TWStat", 126,
    ("fid", fields.uint32l),
    ("stat", stat)
)

RWStat = message_type(
    "RWStat", 127
)


TOpenFD = message_type(
    "TOpenFD", 98,
    ("fid", fields.uint32l),
    ("mode", fields.uint8)
)

ROpenFD = message_type(
    "ROpenFD", 99,
    ("qid", qid),
    ("iounit", fields.uint32l),
    ("unixfd", fields.uint32l)
)
