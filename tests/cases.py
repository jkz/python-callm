import functools
import time
import unittest

from . import dummy

from callm import Stream
from callm import Response

class CallmTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = dummy.Connection('www.dummy.com')
        self.conn = Connection()
        self.conn.host = 'www.dummy.com'

    def tearDown(self):
        self.conn = None

class TestRequest(CallmTestCase):
    def test_basic(self):
        callm = functools.partial(Request, self.conn, mode='url')
        self.assertEqual(callm().foo(), 'http://www.dummy.com/foo')
        self.assertEqual(callm()(123), 'http://www.dummy.com/123')
        self.assertEqual(callm().foo(123), 'http://www.dummy.com/foo/123')
        self.assertEqual(callm().foo('123'), 'http://www.dummy.com/foo123')

    def test_suspend(self):
        callm = Request(self.conn, 'GET', mode='suspend').foo.bar()
        self.assertEqual(callm(mode='url'), 'http://www.dummy.com/foo/bar')
        first = callm().raw
        second = callm().raw
        self.assertEqual(first, second)

class TestResponse(CallmTestCase):
    def test_basic(self):
        strdata = "baz"
        strresp = dummy.Response(strdata)
        self.assertEqual(Response(strresp).raw, strdata)
        self.assertRaises(Exception, lambda: Response(strresp).json)

    def test_json(self):
        jsondata = '{"foo": "bar"}'
        jsonresp = dummy.Response(jsondata)
        self.assertEqual(Response(jsonresp).json['foo'], 'bar')
        self.assertEqual(Response(jsonresp).raw, jsondata)


class TestStream(CallmTestCase):
    def test_basic(self):
        return
        callm = Request(self.conn, 'GET')._('/foo/bar')(eggs='spam', mode='suspend')
        client = Stream('www.dummy.com', async=True)
        print 'Starting'
        client.start(callm)
        print 'running...'
        time.sleep(0.01)
        client.stop()
        print 'done'


class TestResource(CallmTestCase):
    def test_basic(self):
        first = Resource('http://www.dummy.com/?eggs=spam#hai', foo='bar')
        second = Resource('https://www.wrong.com/?eggs=quux&foo=baz#bai',
                      secure=False,
                      host='www.dummy.com',
                      path='/',
                      fragment='hai',
                      query={'eggs': 'spam'},
                      foo='bar')
        self.assertEqual(str(first), str(second))


from callm.connections import Connection
from callm.requests import Request
from callm.resources import Resource
