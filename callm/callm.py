class Callm(dict):
    """
    Base class converts chained attribute gets into an url. When called,
    returns the httpresponse for the request url submitted to a connection.
    Connection can be a httplib connection class or a CallmClient.

    Subclasses dict to store parameters in a dictionary fashion, so the sleek
    Callm syntax is unhindered.

    """
    def __init__(
            self,
            connection,
            method = 'GET',
            auth = None,
            mode = 'call',
            secure = False,
            headers = {},
            query = {}):
        super(Callm, self).__init__(
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
        Extend the query url by supplied part.
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

            if method == 'POST' and False:
                if not body:
                    body = QueryString(query, **kwargs)

            # Build the Burl object that represents the resource identifier
            self['burl'] = Burl(
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

            request = (method, self['burl'].url, body, headers)
            if auth is not None:
                request = auth(*request)
                self['burl'] = Burl(request[1])

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
            return self['burl'].url

        elif mode == 'burl':
            return self['burl']

    def _unicode__(self):
        return unicode(self['request'])

from .burl import Burl, QueryString
