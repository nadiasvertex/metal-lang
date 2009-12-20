import unittest

import stream
import literals

class TestLiterals(unittest.TestCase):
	def setUp(self):
		self.s = stream.new()
		
	def testMatchLiteralInt(self):
		data="249658370"
		self.s.merge(data, "literal_int_test_data")
		rv=literals.l_int(s)
		
		self.assertNotEqual(None, rv)
		self.assertEqual(rv["value"], data)
		