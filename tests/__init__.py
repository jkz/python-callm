import unittest

from . import cases

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(cases.TestRequest),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestResponse),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestStream),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestResource),
])

def run():
    return unittest.TextTestRunner(verbosity=2).run(suite)
