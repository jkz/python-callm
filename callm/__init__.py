"""A fancy urlib and httplib wrapper developed mainly for calling RESTful APIs in style."""

from .response import Responsm
from .connection import Connector
from .error import Error
from .callm import Callm
from .burl import Burl, Url, Uri
from .streaming import Creek, Listener
