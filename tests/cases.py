import functools
import time
import unittest

from . import dummy

from callm.streaming import CreekClient
from callm.response import Responsm

class CallmTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = dummy.Connection('www.dummy.com')
        self.conn = CallmInterface()
        self.conn.host = 'www.dummy.com'

    def tearDown(self):
        self.conn = None

class TestCallm(CallmTestCase):
    def test_basic(self):
        callm = functools.partial(Callm, self.conn, mode='url')
        self.assertEqual(callm().foo(), 'http://www.dummy.com/foo')
        self.assertEqual(callm()(123), 'http://www.dummy.com/123')
        self.assertEqual(callm().foo(123), 'http://www.dummy.com/foo/123')
        self.assertEqual(callm().foo('123'), 'http://www.dummy.com/foo123')

    def test_suspend(self):
        callm = Callm(self.conn, 'GET', mode='suspend').foo.bar()
        self.assertEqual(callm(mode='url'), 'http://www.dummy.com/foo/bar')
        first = callm().raw
        second = callm().raw
        self.assertEqual(first, second)

class TestResponsm(CallmTestCase):
    def test_basic(self):
        strdata = "baz"
        strresp = dummy.Response(strdata)
        self.assertEqual(Responsm(strresp).raw, strdata)
        self.assertRaises(Exception, lambda: Responsm(strresp).json)

    def test_json(self):
        jsondata = '{"foo": "bar"}'
        jsonresp = dummy.Response(jsondata)
        self.assertEqual(Responsm(jsonresp).json['foo'], 'bar')
        self.assertEqual(Responsm(jsonresp).raw, jsondata)


class TestCreek(CallmTestCase):
    def test_basic(self):
        return
        callm = Callm(self.conn, 'GET')._('/foo/bar')(eggs='spam', mode='suspend')
        client = CreekClient('www.dummy.com', async=True)
        print 'Starting'
        client.start(callm)
        print 'running...'
        time.sleep(0.01)
        client.stop()
        print 'done'


class TestBurl(CallmTestCase):
    def test_basic(self):
        first = Burl('http://www.dummy.com/?eggs=spam#hai', foo='bar')
        second = Burl('https://www.wrong.com/?eggs=quux&foo=baz#bai',
                      secure=False,
                      host='www.dummy.com',
                      path='/',
                      fragment='hai',
                      query={'eggs': 'spam'},
                      foo='bar')
        self.assertEqual(str(first), str(second))

class TestAuth(CallmTestCase):
    def test_basic(self):
        class MyAuth(Auth):
            def __call__(self, burl, method='GET', body='', headers={}):
                headers['kitten'] = 'bacon'
                burl.query['puppy'] = 'cake'
        self.conn.auth = MyAuth() 
        callm = self.conn.GET(mode='suspend')
        print callm(mode='url')
        print callm['request']
        
        

from callm.connection import CallmInterface
from callm.callm import Callm
from callm.burl import Burl
from callm.auth import Auth
