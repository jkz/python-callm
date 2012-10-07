class Client(object):
    """
    A service client that authenticates requests as a registered end-user.
    """
    def authenticate(self, **creds):
        """
        Should return an end-user representation on succes, else None
        """
        return None


class EndUser(object):
    """
    An end-user that has authorized a client to authenticate in its name.
    """
    pass

class Auth(object):
    client = None
    enduser = None

    def __call__(self, method, uri, body='', headers=None):
        """
        Make all required modifications and additions to a request for
        authentication. Mimics the http request interface, which allows:

        connection.request(*auth(method, uri, body, headers))
        
        and

        params = auth(*params)
        """
        return method, uri, body, headers
