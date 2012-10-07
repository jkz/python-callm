import functools
import time
import socket
import threading

from .connection import CallmInterface
from .error import CreekError

class CreekListener(object):
    def on_data(self, data):
        print data
        return True

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        return False

    def on_timeout(self):
        """Called when stream connection times out"""
        return True

class Creek(CallmInterface):
    """
    A Callm stream client.
    """
    auto_connect = False
    timeout = 300.0
    retry_count = None
    snooze_time = 5.0
    buffer_size = 1500
    secure = True
    mode = 'stream'
    streaming = True


    running = False
    endpoint = None
    _response = None

    def retry_time(self, error_count):
        return 10.0

    def read(self, amount):
        if not self.running or self.response.isclosed():
            return None
        return self.response.read(amount)

    def readline(self, delimiter='\r\n'):
        if not self.running or self.response.isclosed():
            return None
        return self.response.readline(delimiter)

    from apps.utils.decorators import shoutout
    @shoutout
    def _run(self):
        # Connect and process the stream
        error_counter = 0
        exception = None

        self.connect()
        print 'connected, running:', self.endpoint
        while self.running:
            if self.retry_count is not None and error_counter > self.retry_count:
                break
            try:
                print 'ITER'
                resp = self.endpoint()
                print resp.status
                if resp.status != 200:
                    if self.listener.on_error(resp.status, error_counter) is False:
                        break
                    error_counter += 1
                    time.sleep(self.retry_time(error_counter))
                else:
                    error_counter = 0
                    self._read_loop(resp)
            except socket.timeout:
                print 'TIMEOUT'
                if self.listener.on_timeout() == False:
                    break
                if not self.running:
                    break
                self.reconnect(self.snooze_time)
            except Exception, exception:
                print 'EXCEPTION'
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        self.disconnect()

        if exception:
            raise

    def _read_loop(self, response):
        self.response = response
        while self.running and not response.isclosed():
            data = self.read_loop_iter()
            if self.listener.on_data(data) is False:
                self.running = False
        self.response = None

        if response.isclosed():
            self.on_closed(response)

    @property
    def stream(self):
        self._cache('mode', 'stream')
        return self

    from apps.utils.decorators import shoutout
    @shoutout
    def start(self, callm=None, async=False):
        """Open a stream with a callm request."""
        if callm:
            self.endpoint = callm
        if self.running is True:
            raise CreekError('Stream running already!')
        self.running = True
        print 'RUNNING'
        if async:
            threading.Thread(target=functools.partial(self._run)).start()
        else:
            self._run()

    def stop(self):
        """Close the running stream on this Creek."""
        self.running = False

    def on_closed(self, response):
        """Called when the response has been closed by the host."""
        pass

    def read_loop_iter(self):
        """
        Return one packet of data read from the response. Should normally be
        overwritten by subclass.
        """
        c = ''
        data = ''
        while c != '\n':
            c = self.read(1)
            data += c
        return data

class CreekClient(Creek):
    def __init__(self, host, listener=None, auth=None, **options):
        self.host = host
        self.listener = listener or CreekListener()
        self.auth = auth

        OPTIONS = ("timeout", "retry_count", "retry_time",
                   "snooze_time", "buffer_size", "secure",)

        for key in OPTIONS:
            setattr(self, key, options.get(key, getattr(self, key)))
