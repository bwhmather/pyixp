from pyixp import messages


class Request(object):
    serialize = False

    def __init__(self, *args, **kwargs):
        self._request = self.request_type(*args, **kwargs).pack()

    def _parse_response(self, type_id, response):
        if type_id == response_type.type_id:
            return self.response_type.unpack(response)

        elif type_id == messages.RError.type_id:
            raise messages.RError.unpack(response)

        else:
            raise Exception("unrecognized type id")


    def submit(marshall):
        response = marshall.request(self.request_type.type_id,
                                    self._request,
                                    self.serialize)

        return self._parse_response(*response)

    def submit_async(marshall, on_success, on_error):
        def _on_success(type_id, response):
            try:
                response = self._parse_response(type_id, response)
            except Exception as e:
                on_error(e)
                return
            on_success(response)

        marshall.request_async(self.request_type.type_id,
                               self._request,
                               _on_success, on_error,
                               self.sequential)


class VersionRequest(Request):
    request_type = messages.TVersion
    response_type = messages.RVersion
    serialize=True

class AuthRequest(Request):
    request_type = messages.TAuth
    response_type = messages.RAuth

class AttachRequest(Request):
    request_type = messages.TAttach
    response_type = messages.RAttach

class FlushRequest(Request):
    request_type = messages.TFlush
    response_type = messages.RFlush

class WalkRequest(Request):
    request_type = messages.TWalk
    response_type = messages.RWalk

class OpenRequest(Request):
    request_type = messages.TOpen
    response_type = messages.ROpen

class CreateRequest(Request):
    request_type = messages.TCreate
    response_type = messages.RCreate

class ReadRequest(Request):
    request_type = messages.TRead
    response_type = messages.RRead

class WriteRequest(Request):
    request_type = messages.TWrite
    response_type = messages.RWrite

class ClunkRequest(Request):
    request_type = messages.TClunk
    response_type = messages.RClunk

class RemoveRequest(Request):
    request_type = messages.TRemove
    response_type = messages.RRemove

class StatRequest(Request):
    request_type = messages.TStat
    response_type = messages.RStat

class WStatRequest(Request):
    request_type = messages.TWStat
    response_type = messages.RWStat

class OpenFDRequest(Request):
    request_type = messages.TOpenFD
    response_type = messages.ROpenFD
