import urlparse
import urllib

from .connection import Connection

class Burl(object):
    """
    A flexible url builder class. Deconstructs a given url into parts, then
    sets or replaces parts by explicitly passed parts.

    Usage example:

    >>> Burl('

    >>> Burl('example.com/foo?kitten=cake', host='otherhost.net',
    ...         kitten='fluffy', secure=True).url
    https://otherhost.net/foo?kitten=fluffy


    One should change the following attributes on the bound connection:
        secure
        scheme
        host
        port

    Heads up!

    Does not support duplicate query keys
    """
    #XXX: A normalize method would be nice
    #TODO: encoding check
    def __init__(self,
            url=None,
            connection=None,
            scheme=None,
            host=None,
            port=None,
            path=None,
            fragment=None,
            query=None,
            query_string=None,
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
        return QueryString(self.query, self.verbatim)

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

    def __call__(self, **kwargs):
        self.connection()(self.uri, **kwargs)

class Url(str):
    def __new__(self, *args, **kwargs):
        burl = Burl(*args, **kwargs)
        return str.__new__(self, burl.url)

class Uri(str):
    def __new__(self, *args, **kwargs):
        burl = Burl(*args, **kwargs)
        return str.__new__(self, burl.uri)

class QueryString(str):
    def __new__(self, query, verbatim=False, **kwargs):
        """
        Heads up!

        Does not support duplicate keys.
        """
        query_cpy = query.copy()
        query_cpy.update(kwargs)
        if verbatim:
            return '&'.join(('='.join(map(str, (k, v))) for k, v in self.query.iteritems()))
        else:
            return urllib.urlencode(query_cpy)

