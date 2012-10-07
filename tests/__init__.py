import unittest

from . import cases

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(cases.TestCallm),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestResponsm),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestCreek),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestBurl),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestAuth),
])

def run():
    return unittest.TextTestRunner(verbosity=2).run(suite)
