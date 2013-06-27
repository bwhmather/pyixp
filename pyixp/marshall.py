import logging
import socket
import struct

from threading import Thread, Condition
from queue import Queue, LifoQueue

__all__ = 'Marshall',

log = logging.getLogger(__name__)

_header = struct.Struct("<IbH")


def recvall(socket, n):
    """ Read exactly n bytes from a socket
    """
    data = bytearray(n)
    window = memoryview(data)
    while len(window):
        try:
            read = socket.recv_into(window)
            if read == 0:
                raise EOFError('unexpected end of file')
            window = window[read:]
        except InterruptedError:
            continue
    # TODO would be nice if this could be done without a copy (not that it
    # makes any real difference)
    return bytes(data)


class Marshall(object):
    """ Serialises sending of packets and associates them with their
    corresponding responses.
    """
    _NOTAG = 0xffff

    def __init__(self, socket, maxrequests=1024):
        """
        :param socket:  connection to the server.  The socket will be closed by
            the marshall on shutdown.

        :param maxrequests: sets an upper limit on the number of requests that
            can be sent to the server without receiving a response.  Requests
            made beyond the limit will not be dropped but will instead wait for
            an earlier request to finish.  Maximum possible value is 65535.
        :type maxrequests: unsigned 16bit integer (0 <= maxtag <= 65535)
        """
        self._socket = socket

        # queue of ``(type, request, on_error, on_success, sequential)`` tuples
        # for passing requests to the send thread.  Adding false to the queue
        # will cause the send loop to exit
        self._send_queue = Queue()

        # queue of booleans used as a counter for the number of remaining
        # responses and stop the receive loop blocking on recv if no message is
        # expected
        # True indicates that a request has been sent and to expect a reply
        # False indicates that the receive loop should quit immediately
        self._recv_queue = Queue()

        # stack of available transaction tags that can be assigned to new
        # requests.
        # tags are used to identify the request that a response corresponds to.
        self._tags = LifoQueue(maxsize=maxrequests)
        for tag in range(1, maxrequests):
            self._tags.put(tag)

        # map from transaction tags (uint16) to completion callbacks
        self._callbacks = {}

        # responses to callbacks without tags are dispatched in the same order
        # the as the requests were submitted
        self._sequential_callbacks = Queue()

        self._send_thread = Thread(target=self._send_loop, daemon=True)
        self._send_thread.start()

        self._recv_thread = Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _do_send(self, request_type, request,
                 on_success, on_error,
                 sequential):

        if not sequential:
            # bind the callback to a new tag.
            # self._tags.get() should block until a tag becomes available.
            tag = self._tags.get()
            assert tag not in self._callbacks
            self._callbacks[tag] = (on_success, on_error,)
        else:
            tag = self._NOTAG
            self._sequential_callbacks.put((on_success, on_error,))

        header = _header.pack(len(request)+_header.size, request_type, tag)

        self._socket.sendall(header)
        self._socket.sendall(request)

    def _send_loop(self):
        """ loop for sending packets
        """
        while True:
            try:
                task = self._send_queue.get()

                # if task is False, shut down
                if not task:
                    log.info("quiting send loop")
                    return

                self._do_send(*task)

                # if nothing went wrong, notify the recv loop that another
                # response message is expected
                self._recv_queue.put(True)

                self._send_queue.task_done()

            except Exception as error:
                log.exception("error in send thread", stack_info=True)
                self.close(error)
                return

    def _do_recv(self):
        header = recvall(self._socket, _header.size)
        length, type_, tag = _header.unpack(header)
        if length < _header.size:
            raise Exception("invalid frame length: %i" % length)

        body = recvall(self._socket, length - _header.size)

        if tag == self._NOTAG:
            on_success, on_error = self._sequential_callbacks.get()
        else:
            # retrieve callback and return tag to free list
            on_success, on_error = self._callbacks.pop(tag)
            self._tags.put(tag)

        try:
            on_success(type_, body)
        except:
            log.exception("exception in user callback", stack_info=True)

    def _recv_loop(self):
        """ loop for receiving packets
        """
        while True:
            try:
                if not self._recv_queue.get():
                    log.info("quiting receive loop")
                    return

                self._do_recv()

                self._recv_queue.task_done()

            except Exception as e:
                log.exception("error in receive thread", stack_info=True)
                self.close(e)
                return

    def request(self, request_type, request, sequential=False):
        """
        """
        cond = Condition()
        # dict is used as reference type to allow result to be returned from
        # seperate thread
        response_cont = {}

        def on_success(response_type, response):
            response_cont.update({
                "success": True,
                "type": response_type,
                "response": response,
            })
            with cond:
                cond.notify()

        def on_error(exception):
            response_cont.update({
                "success": False,
                "exception": exception,
            })
            with cond:
                cond.notify()

        with cond:
            self.request_async(request_type, request,
                               on_success, on_error,
                               sequential)
            cond.wait()

        if not response_cont["success"]:
            raise response_cont["exception"]

        return response_cont["type"], response_cont["response"]

    def request_async(self, request_type, request,
                      on_success, on_error=None,
                      sequential=False):
        """ Send a 9p request to the server and wait for a response

        :param packet: the contents of the packet to send to the server.
        :type packet: bytestring

        :param on_success: type -> bytes -> void
        :param on_error: Exception -> void

        :sequential: send request with no tag.  responses to untagged requests
            are sent in the order that the requests were received

        :returns: bytestring -- The reply recieved from the server or nothing
            if a callback was provided.
        """
        log.info("request")

        self._send_queue.put((request_type, request,
                              on_success, on_error,
                              sequential,))

    def shutdown(self):
        """ Attempt to gracefully shut down the server
        """
        log.info("shutting down multiplexer")

        # stop anything else from adding requests to the send queue.  sorry.
        # a reference to the put method is kept so that a quit signal can be
        # sent after all requests are handled.
        def raise_marshall_closed_error(*args, **kwargs):
            raise Exception("marshall closed")

        send_queue_put = self._send_queue.put
        self._send_queue.put = raise_marshall_closed_error

        # wait for send queue to empty
        self._send_queue.join()

        # tell the send thread to quit then wait for it to do so
        send_queue_put(False)
        self._send_thread.join()

        # likewise for receive
        self._recv_queue.put(False)
        self._recv_thread.join()

        # close socket
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

        for on_success, on_error in self._callbacks.values():
            try:
                on_error(Exception("shutdown"))
            except:
                log.exception("exception in user callback", stack_info=True)

        log.info("successfully shut down multiplexer")

    def close(self, error=None):
        """ Immediately close the socket and cancel all remaining callbacks
        without any ceremony. ``shutdown`` should be prefered in most cases

        :param error: passed as the error argument to all remaining callbacks
        :type Exception:
        """
        log.info("terminating multiplexer")

        self._socket.close()

        # neither loop will notice that the socket is closed unless it is
        # working on something so it is still necessary to send quit signals
        self._send_queue.put(False)
        self._recv_queue.put(False)

        for on_success, on_error in self._callbacks.values():
            try:
                on_error(Exception("close"))
            except:
                log.exception("exception in user callback", stack_info=True)

        log.info("successfully terminated multiplexer")
