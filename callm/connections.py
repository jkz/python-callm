import httplib
import time

from .responses import Response

class Connection(object):
    """
    An ABC mixin providing http request method calls.

    Requires the inheritor to have a domain string field.

    Examples usage:
    obj.url.http.GET.path.to.page()
    obj.suspend.https.POST('/some/path')

    Let's compare

    >>> # Our parameters
    >>> resource='/cat/<uid>/kitten?cake=<something>'
    >>> domain = example.com
    >>> uid = 123
    >>> cake = 'delicious'
    >>> # Here's how you do it
    >>> from httplib import HttpConection
    >>> from urllib import urlunsplit
    >>> from urlparse import urlencode
    >>> from json import loads
    >>> conn = HttpConnection(domain)
    >>> qs = urlencode({'cake': cake})
    >>> path = '/cat/%s/kitten'
    >>> uri = urlunsplit(None, None, path, qs, None)
    >>> conn.request(uri=uri)
    >>> resp = conn.get_responses()
    >>> data = loads(resp.read())
    >>> # Or if you feel like it:
    >>> conn = HttpConnection(domain)
    >>> conn.request(urlunsplit(none, none, '/cat/%s/kitten' % uid, urlencode({'cake': cake}), none)
    >>> data = loads(conn.get_responses().read())
    >>> # Here's how I do it
    >>> from callm.connector import Connection
    >>> data = Connection(domain).GET.cat.uid.kitten(uid=uid, cake=cake).json
    >>> # Or this way
    >>> data = Connection(domain).json.GET.cat._(uid).kitten(cake=cake)
    >>> # Or like that!
    >>> path = '/cat/%s/kitten'
    >>> data = Connection(domain).GET(path, cake=cake).json
    >>> # Lol, while you're still struggling for you request, I made 3 already
    """
    host = None
    auth = None
    secure = False
    method = 'GET'
    auto_connect = True
    mode = 'call'
    format = None
    streaming = False

    # scheme = 'http'
    port = None
    strict = False
    timeout = 5.0  # seconds
    reconnect_time = 5.0  #seconds

    headers = {}

    connection = None

    auto_callm = False

    def __init__(self, host=None, **kwargs):
        if host:
            self.host = host
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def netloc(self):
        if (self.port is not None
        and not (self.port == 80 and self.scheme == 'http')
        and not (self.port == 443 and self.scheme == 'https')):
            return ':'.join((self.host, str(self.port)))
        else:
            return self.host

    @property
    def scheme(self):
        if self.secure:
            return 'https'
        else:
            return 'http'

    def connect(self, host=None, port=None, timeout=None, strict=None):
        """
        Open the appropriate connection with the specified host.
        """
        # Return if the connection is opened already
        if self.connection is not None:
            return

        # Specify the connection type
        if self.secure:
            connector = httplib.HTTPSConnection
        else:
            connector = httplib.HTTPConnection

        # Prepare parameters
        params = {}
        for attr in ('host', 'port', 'strict', 'timeout'):
            val = locals().get(attr)
            params[attr] = getattr(self, attr) if val is None else val

        # Open the connection
        self.connection = connector(**params)

    def reconnect(self, reconnect_time=None):
        """
        Disconnect and then connect after sleeping passed or default seconds.
        """
        self.disconnect()
        if reconnect_time is None:
            reconnect_time = self.reconnect_time
        time.sleep(reconnect_time)
        self.connect()

    def disconnect(self):
        """
        Close the connection if it is open.
        """
        if self.connection is None:
            return
        self.connection.close()
        self.connection = None

    def request(self, method, url, body=None, headers={}):
        """
        Thin wrapper around httplib request, opening a connection if needed.
        """
        # Open a connection if it is not manually handled
        if self.auto_connect:
            self.connect()
        _headers = self.headers.copy()
        _headers.update(headers)
        params = (method, Resource(url).uri, body, _headers)
        self.connection.request(*params)

    def getresponse(self, **kwargs):
        """
        A wrapper around httplib getresponse. Returns a Reponsm instance,
        potentially in a predifined format.
        """
        _response = self.connection.getresponse()
        response = Response(_response, self.streaming)
        # Close the connection if it is not manually handled
        if self.auto_connect:
            self.disconnect()
        # Return formatted if specified
        format = kwargs.pop('format', self._flush('format'))
        if format:
            return getattr(response, format)
        return response

    #XXX: needs work on arguments
    def fetch(self, *args, **kwargs):
        self.request(*args, **kwargs)
        return self.getresponse()

    def _cache(self, attr, val):
        setattr(self, '_' + attr, val)

    def _flush(self, attr):
        try:
            val = getattr(self, '_' + attr)
        except AttributeError:
            val = getattr(self, attr)
        else:
            delattr(self, '_' + attr)
        finally:
            return val

    @property
    def call(self):
        self._cache('mode', 'call')
        return self

    @property
    def suspend(self):
        self._cache('mode', 'suspend')
        return self

    @property
    def url(self):
        self._cache('mode', 'url')
        return self

    @property
    def json(self):
        self._cache('format', 'url')
        return self

    @property
    def http(self):
        self._cache('secure', False)
        return self

    @property
    def https(self):
        self._cache('secure', True)
        return self

    def build_callm(self, *args, **kwargs):
        """
        Return a Callm constructor with provided connection and auth.
        """
        method = kwargs.pop('method', self._flush('method'))
        secure = kwargs.pop('secure', self._flush('secure'))
        mode = kwargs.pop('mode', self._flush('mode'))
        format = kwargs.pop('format', None)
        if format is not None:
            self._cache('format', format)
        return Request(*args, connection=self, auth=self.auth, method=method,
                secure=secure, mode=mode)

    @property
    def callm(self):
        return self.build_callm()

    @property
    def GET(self):
        return self.build_callm(method='GET')

    @property
    def POST(self):
        return self.build_callm(method='POST')

    @property
    def UPDATE(self):
        return self.build_callm(method='UPDATE')

    @property
    def DELETE(self):
        return self.build_callm(method='DELETE')

    @property
    def HEAD(self):
        return self.build_callm(method='HEAD')

# Circumvent circular circumstance
from .requests import Request
from .resources import Resource
