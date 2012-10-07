"""A fancy urlib and httplib wrapper developed mainly for calling RESTful APIs in style."""

from .response import Responsm
from .connection import CallmInterface as Connector
from .error import CallmError, CallmHTTPError
from .callm import Callm
from .burl import Burl, Url, Uri
from .auth import Auth, Client, EndUser
from .streaming import Creek, CreekListener
