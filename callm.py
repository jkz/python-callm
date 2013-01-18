"""
A sexy urllib and httplib wrapper build to interact with (restful) web API's.

DOES NOT SUPPORT DUPLICATE KEYS.

Contents:
    Error
    HTTPError

    Resource
    URL
    URI
    Query
    Request
    Response
    Connection
    Stream
    Listener
"""

import urlparse
import urllib
import httplib
import json
import xml.dom.minidom
import functools
import time
import socket
import threading


class Error(Exception):
    pass


class HTTPError(Error):
    def __init__(self, e, uri, format, uriparts):
        self.e = e
        self.uri = uri
        self.format = format
        self.uriparts = uriparts
        self.response_data = self.e.fp.read()

    def __str__(self):
        fmt = ("." + self.format) if self.format else ""
        return (
            "Server sent status %i for URL: %s%s using parameters: "
            "(%s)\ndetails: %s" %(
                self.e.code, self.uri, fmt, self.uriparts,
                self.response_data))



class Query(str):
    """A querystring builder class.

    Turns keyword arguments into a urlencoded querystring.

    query -- a dictionary or sequence of pair tuples
    verbatim -- turns off urlencoding when True
    """
    def __new__(self, query=(), verbatim=False, **kwargs):
        pairs = []
        try:
            pairs.extend(query.items())
        except AttributeError:
            pairs.extend(query)
        pairs.extend(kwargs.items())
        if verbatim:
            return '&'.join(('='.join(map(str, p)) for p in pairs))
        else:
            return urllib.urlencode(pairs)


class Resource(object):
    """
    A flexible url builder class. Deconstructs a given url into parts, then
    sets or replaces parts by explicitly passed parts.

    Usage example:

    >>> Burl('example.com/foo?kitten=cake', host='otherhost.net',
    ...         kitten='fluffy', secure=True).url
    https://otherhost.net/foo?kitten=fluffy
    """
    #XXX: A normalize method would be nice
    #XXX: userinfo would be nice
    #TODO: encoding check
    def __init__(self,
            url=None,
            connection=None,
            scheme=None,
            host=None,
            port=None,
            path=None,
            query=None,
            query_string=None,
            fragment=None,
            secure=None,
            verbatim=False,
            **kwargs
    ):
        # Determines whether paramters are combined encoded or verbatim
        self.verbatim = verbatim

        if url is None:
            url = ''

        # Split the url into scheme, port, host, query and path
        _scheme, _netloc, self.path, _query_string, self.fragment = urlparse.urlsplit(url)

        # This is the currently used indicator for the scheme, by the callm
        # instance gerating the url.
        self.secure = _scheme == 'https'

        # Set the connection on self to extract parameters and enable requests.
        #XXX: Add a mode that does not alter the connection
        self.connection = connection or Connection()

        _host, _, _port = _netloc.partition(':')

        # Set security level on the connection
        if secure is not None:
            self.connection.secure = secure
        elif _scheme == 'https':
            self.connection.secure = True
        elif _scheme == 'http':
            self.connection.secure = False

        # Set the host
        if host is not None:
            self.connection.host = host
        elif self.connection.host is None:
            self.connection.host = _host

        # Set the port
        if port is not None:
            self.connection.port = port
        elif _port:
            self.connection.port = _port

        # Set the path
        if path is not None:
            self.path = path

        # Set the fragment
        if fragment is not None:
            self.fragment = fragment

        # Create the query dictionary and add kwargs to it
        self.query = {}
        if _query_string is not None:
            self.query.update(dict(urlparse.parse_qsl(_query_string)))
        if query_string is not None:
            self.query.update(dict(urlparse.parse_qsl(query_string)))
        if query is not None:
            self.query.update(query)
        self.query.update(kwargs)

    @property
    def query_string(self):
        return Query(self.query, self.verbatim)

    @property
    def host_parts(self):
        return (self.connection.scheme,
                self.connection.netloc)

    @property
    def uri_parts(self):
        return (self.path,
                self.query_string,
                self.fragment)

    @property
    def parts(self):
        return self.host_parts + self.uri_parts

    @property
    def authority(self):
        return urlparse.urlunsplit(self.host_parts, + (None, None, None))


    #TODO: Name this properly
    @property
    def uri(self):
        """
        Return the url string without scheme and netloc parts
        """
        return urlparse.urlunsplit((None, None) + self.uri_parts)

    @property
    def url(self):
        return urlparse.urlunsplit(self.parts)

    def __str__(self):
        """
        Return a string containing the complete url.
        """
        return self.url

    def __call__(self, *args, **kwargs):
        #urllib.urlopen(self.url, *args, **kwargs)
        #self.connection()(self.uri, *args, **kwargs)
        return Request(self.connection)(self.uri, *args, **kwargs)


class URL(str):
    def __new__(self, *args, **kwargs):
        resource = Resource(*args, **kwargs)
        return str.__new__(self, resource.url)


class URI(str):
    def __new__(self, *args, **kwargs):
        resource = Resource(*args, **kwargs)
        return str.__new__(self, resource.uri)


class Endpoint(list):
    """
    Represents a partial request object. That fires when called.

    Desired usage:

    conn = Conn('foo.com')
    conn.GET('/users/%s' % id).response
    conn.GET('/users/%s' % id).raw
    conn.GET('/users/%s' % id).html
    conn.GET('/users/%s' % id).json
    conn.GET('/users/%s' % id).debug

    class API(Connection):
        host = 'example.com'
        format = 'json'

        def me(self):
            return self.GET('/me')

        def my_tracks(self):
            return self.me
    """
    METHOD, URL, BODY, HEADERS = range(4)
    def __init__(self,
            connection=None,
            path='',
            method='GET',
            query=None,
            headers=None,
            body=None,
            **kwargs):
        if isinstance(connection, basestring):
            self.connection = Connection(connection)

    def update(self, path, query=None, headers=None, body=None, **kwargs):


    def __call__(self):
        pass

class Request(object):
    """
    Represents a request
    """
    def __init__(self,

class Request(dict):
    """
    Base class converts chained attribute gets into an url. When called,
    returns the httpresponse for the request url submitted to a connection.
    Connection can be a httplib connection class or a CallmClient.

    Subclasses dict to store parameters in a dictionary fashion, so the sleek
    Callm syntax is unhindered.

    """
    class Error(Error): pass

    def __init__(
            self,
            connection,
            method = 'GET',
            auth = None,
            mode = 'call',
            secure = False,
            headers = {},
            query = {}):
        super(Request, self).__init__(
                connection = connection,
                auth = auth,
                method = method,
                mode = mode,
                secure = secure,
                parts = (),
                is_built = False,
                headers = headers,
                query = query)

    def __getattr__(self, part):
        """
        Extend the request url by supplied part.
        """
        try:
            return object.__getattr__(self, part)
        except AttributeError:
            self['is_built'] = False
            def extend_call(arg):
                self['parts'] += (arg,)
                return self

            # You can manually add a string part by syntax:
            #     api.first._('second').third
            return extend_call if part == '_' else extend_call(part)

    #TODO Cleanup call and do these parameters as __getattr__ on the returned
    #     object.
    def __call__(self,
            tail = '',
            fragment = None,
            body = None,
            mode = None,
            auth = None,
            headers = {},
            query = {},
            **kwargs):
        """
        Resolve the described uri with supplied kwargs. The tail is
        concatenated to the built path. The tail can also be used as the full
        path argument.

        Kwargs replace each first occurance of url parts with matching names.
        All non-mathing kwargs are added to the query dict (overriding
        duplicates)
        """

        # Passed mode gets precedence over attributed mode
        if mode is None:
            mode = self['mode']

        # A Callm saves it's built state so it is only evaluated once. If a
        # change is made to the Callm, this state changes back to False.
        if not self['is_built'] or mode == 'suspend':
            method = self['method'].upper()

            # Combine the path parts, updating matching parts with kwargs
            parts = [str(kwargs.pop(part, part)) for part in self['parts']]

            # When the tail parameter is not a string, treat it as a part
            if not isinstance(tail, basestring):
                end = ''
                parts.append(str(tail))

            # Else split it into an extention and fragment
            else:
                end, _, fragment = tail.partition('#')

            # Build/the/final/path
            uri = '/'.join(parts) + end

            #TODO proper default value here (versioning etc)
            self['headers'].update(headers)
            headers['User-Agent'] = self['headers'].pop('User-Agent', 'callm/0.0.1')
            headers = self['headers']

            if method == 'POST':
                if not body:
                    body = Query(query, **kwargs)
                kwargs = {}

            # Build the Burl object that represents the resource identifier
            self['resource'] = Resource(
                    uri,
                    connection=self['connection'],
                    fragment=fragment,
                    query=query, #if method != 'POST' else None,
                    secure=self['secure'],
                    **kwargs)

            # Select authentication if any
            if auth is not None:
                pass
            elif self['auth'] is not None:
                auth = self['auth']
            else:
                auth = self['connection'].auth

            request = (method, self['resource'].url, body, headers)
            if auth is not None:
                request = auth(*request)
                self['resource'] = Resource(request[1])

            # A 4 tuple suitable for httplib.HTTPConnection.request
            self['request'] = request

            # If unchanged, this callm object will use the url and request
            # built here on subsequent calls
            self['is_built'] = True

        # Return the request object prepared for calling
        if mode == 'suspend':
            self['mode'] = 'call'
            return self

        # Start a stream on given connection
        elif mode == 'stream':
            self['mode'] = 'call'
            self['connection'].start(self)

        # Submit the request and return the response
        elif mode == 'call':
            return self['connection'].fetch(*self['request'])

        # Return a string representation of the url for the request
        elif mode == 'url':
            return self['resource'].url

        elif mode == 'debug':
            return self['request']

        elif mode == 'resource':
            return self['resource']

    def _unicode__(self):
        return unicode(self['request'])


class Connection(object):
    """
    Requires the inheritor to have a domain string field.
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
    def debug(self):
        self._cache('mode', 'debug')
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


class Response(object):
    """
    Response from a callm request.
    Can represent data in different formats by calling the corresponding
    attribute.

    """
    #TODO: Behaviour is not optimal with streaming responses. Perhaps a read()
    #      wrapper should be added with a buffer and an index.
    #TODO: Encoding is not yet handled properly
    #TODO: return format equal to MIME-TYPE header
    class Error(Error): pass

    def __init__(self, response, streaming=False):
        self.response = response
        self.headers = dict(response.getheaders())
        if not streaming:
            self.raw = response.read()

    def __getattr__(self, attr):
        """
        Parameters missing on this class are requested from the http
        response object.
        """
        try:
            return self.__dict__[attr]
        except KeyError:
            return getattr(self.response, attr)

    def readline(self, delimiter='\r\n'):
        """Return data read up to first occurrance of delimiter."""
        data = ''
        while not data.endswith(delimiter):
            data += self.read(1)
        # Exclude delimiter from return data
        return data[:-len(delimiter)]

    @property
    def old_raw(self):
        if not hasattr(self, '_raw'):
          self._raw = self.response.read()
        return self._raw

    @property
    def utf8(self):
        return self.raw.decode('utf8')

    @property
    def html(self):
        return self.utf8

    @property
    def json(self):
        try:
            return json.loads(self.utf8)
        except Exception, e:
            raise self.Error("Could not parse json from data!", e)

    @property
    def xml(self):
        try:
            return xml.dom.minidom.parseString(self.utf8)
        except Exception, e:
            raise self.Error("Could not parse xml from data!", e)

    @property
    def query(self):
        return dict(urlparse.parse_qsl(self.raw))


class Listener(object):
    def on_data(self, data):
        print data
        return True

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        return False

    def on_timeout(self):
        """Called when stream connection times out"""
        return True

class Stream(Connection):
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

    class Error(Error): pass

    def __init__(self, host=None, auth=None, listener=None, **options):
        if host:
            self.host = host
        self.listener = listener or Listener()
        self.auth = auth

        OPTIONS = ("timeout", "retry_count", "retry_time",
                   "snooze_time", "buffer_size", "secure",)

        for key in OPTIONS:
            setattr(self, key, options.get(key, getattr(self, key)))

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

    def start(self, callm=None, async=False):
        """Open a stream with a callm request."""
        if callm:
            self.endpoint = callm
        if self.running is True:
            raise self.Error('Stream running already!')
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

