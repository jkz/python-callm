"""A fancy urlib and httplib wrapper developed mainly for calling RESTful APIs in style."""

from .responses import Response
from .connections import Connection
from .errors import Error
from .requests import Request
from .resources import Resource, URL, URI
from .streams import Stream, Listener

