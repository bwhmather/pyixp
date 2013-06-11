import logging
import socket
from construct import Struct, UBInt16, UBInt32, String, Container, FieldError

from threading import Thread, Condition
from queue import Queue, LifoQueue

__all__ = 'Marshall',

log = logging.getLogger(__name__)


def recvall(socket, n):
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


def recv_packet(socket):
    header = recvall(socket, 4)
    length = UBInt32("length").parse(header[:4])
    if length < 4:
        raise Exception("invalid frame length: %i" % length)

    return recvall(socket, length - 4)


class Marshall(object):
    """ Serialises sending of packets and associates them with their
    corresponding responses.
    """
    _NOTAG = 0

    _packet_format = Struct("packet",
        UBInt32("length"),
        UBInt16("tag"),
        String("body", lambda ctx: ctx.length - 6)
    )

    def __init__(self, socket, maxtag=1024):
        """
        :param socket:  connection to the server.  The socket will be closed by
            the marshall on shutdown.

        :param maxtag: sets an upper limit on the number of requests that can
            be sent to the server without receiving a response.  If there are
            no tags available the send loop will block waiting for a response
            to free one up before sending another request.  Maximum possible
            value is 65535.
        :type maxtag: unsigned 16bit integer (0 <= maxtag <= 65535)
        """
        self._socket = socket

        # queue of ``(data, callback,)`` tuples for submission of requests to
        # the send thread.  Submitting a task which evaluates to False will
        # cause the send loop to exit
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
        self._tags = LifoQueue(maxsize=maxtag)
        for tag in range(1, maxtag):
            self._tags.put(tag)

        # map from transaction tags (uint16) to completion callbacks
        self._callbacks = {}

        self._send_thread = Thread(target=self._send_loop, daemon=True)
        self._send_thread.start()

        self._recv_thread = Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _do_send(self, data, callback, notag):
        # bind the callback to a new tag.
        # self._tags.get() should block until a tag becomes available.
        # if a recoverable error occurs this step will be manually
        # rolled back.
        if not notag:
            tag = self._tags.get()
        else:
            tag = self._NOTAG

        try:
            packet = self._packet_format.build(Container(
                length=len(data)+6,
                tag=tag,
                body=data
            ))

        except (FieldError, TypeError) as error:
            # errors while building a packet are generally a consequence of
            # invalid user input and should not be fatal
            if tag != self._NOTAG:
                self._tags.put(tag)

            try:
                callback(None, error)
            except:
                log.exception("exception in user callback", stack_info=True)

            return

        assert tag not in self._callbacks
        self._callbacks[tag] = callback

        self._socket.sendall(packet)

        # if nothing went wrong, notify the recv loop that another
        # response message is expected
        self._recv_queue.put(True)

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

                self._send_queue.task_done()

            except Exception as error:
                log.exception("error in send thread", stack_info=True)
                self.close(error)

    def _do_recv(self):

        # read and parse packet
        body = recv_packet(self._socket)
        log.debug("packet received")

        tag = UBInt16("tag").parse(body[:2])
        body = body[2:]

        # retrieve callback and return tag to free list
        callback = self._callbacks.pop(tag)
        self._tags.put(tag)

        try:
            callback(body, None)
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

    def _request_sync(self, packet, notag):
        cond = Condition()
        # dict is used as reference type to allow result to be returned from
        # seperate thread
        response_container = {}

        def callback(response, error=None):
            # store result
            response_container.update(dict(response=response, error=error))
            # wake up waiting thread
            with cond:
                cond.notify()

        with cond:
            self.request(packet, callback, notag)
            cond.wait()

            if response_container["error"]:
                raise response_container["error"]

            return response_container["response"]

    def request(self, packet, callback=None, notag=False):
        """ Send a 9p request to the server and wait for a response

        :param packet: the contents of the packet to send to the server.
        :type packet: bytestring

        :param callback: if provided the request will be executed
            asynchronously.  If the request is successfull the callback will be
            called with a bytes() object containing the contents of the
            response packet as it's first argument and None as it's second.
            If an error occurs the first argument will contain None and the
            second an Exception() object describing the error.

        :returns: bytestring -- The reply recieved from the server or nothing
            if a callback was provided.
        """
        if callback is None:
            # request sync adds a default callback the recalls request
            return self._request_sync(packet, notag)

        log.info("request")

        self._send_queue.put((packet, callback, notag,))

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

        for callback in self._callbacks.values():
            try:
                callback(None, None)
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
        # working on something
        self._send_queue.put(False)
        self._recv_queue.put(False)

        self._send_thread.join()
        self._recv_thread.join()

        for callback in self._callbacks.values():
            try:
                callback(None, error)
            except:
                log.exception("exception in user callback", stack_info=True)

        log.info("successfully terminated multiplexer")
