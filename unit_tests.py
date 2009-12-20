import unittest

import expr
import mparser
import typesys
from gen import llvm 


suite = unittest.TestLoader().loadTestsFromModule(typesys.tests)
unittest.TextTestRunner(verbosity=2).run(suite)

suite = unittest.TestLoader().loadTestsFromModule(expr.tests)
unittest.TextTestRunner(verbosity=2).run(suite)

suite = unittest.TestLoader().loadTestsFromModule(mparser.tests)
unittest.TextTestRunner(verbosity=2).run(suite)

# These tests can take a very long time, so you may want to
# disable them while developing.
suite = unittest.TestLoader().loadTestsFromModule(llvm.tests)
unittest.TextTestRunner(verbosity=2).run(suite)