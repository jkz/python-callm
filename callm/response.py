import json
import urlparse
import xml.dom.minidom

from .error import ResponsmError

class Responsm(object):
    """
    Response from a callm request.
    Can represent data in different formats by calling the corresponding
    attribute. 

    TODO: Behaviour is not optimal with streaming responses. Perhaps a read()
    wrapper should be added with a buffer and an index.
    TODO: Encoding is not yet handled properly
    """
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
            raise ResponsmError("Could not parse json from data!", e)

    @property
    def xml(self):
        try:
            return xml.dom.minidom.parseString(self.utf8)
        except Exception, e:
            raise ResponsmError("Could not parse xml from data!", e)

    @property
    def query(self):
        return dict(urlparse.parse_qsl(self.raw))
