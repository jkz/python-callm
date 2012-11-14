class Error(Exception):
    pass

class HTTPError(Error):
    """
    Exception thrown by the Callm object when there is an
    HTTP error interacting with a restful server
    """
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

