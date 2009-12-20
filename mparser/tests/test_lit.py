import err
import sys
import unittest

import mparser.stream
from mparser import literals

class TestLiterals(unittest.TestCase):
    def setUp(self):
        self.s = mparser.stream.new()
        self.log = err.new(sys.stderr)
        
    def testMatchLiteralInt(self):
        "Try to parse a literal integer."
        
        data="249658370"
        self.s.merge(data, "literal_int_test_data")
        rv=literals.l_int_expr(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(rv.value, int(data))
    
    def testMatchLiteralFloat(self):
        "Try to parse a literal floating point value."
        
        data="1249658370.375912468"
        self.s.merge(data, "literal_float_test_data")
        rv=literals.l_float_expr(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(rv.value, float(data))
        
    def testMatchIdent(self):
        "Try to parse an identifier."
        
        data="the_dog_AND_1_Cat"
        self.s.merge(data, "literal_ident_test_data")
        rv=literals.l_ident(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(rv["ident"], data)
        
        data="10this_and_that"
        self.s.merge(data, "literal_ident_test_data2")
        rv=literals.l_ident(self.s, self.log)
        
        self.assertEqual(None, rv)
        
    def testMatchString(self):
        "Try to parse a string." 
        
        data="'a short string'"
        self.s.merge(data, "literal_sq_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(data[1:-1], rv["value"])
        
        data='"another short string"'
        self.s.merge(data, "literal_dq_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(data[1:-1], rv["value"])
        
        data='"""a long string"""'
        self.s.merge(data, "literal_dq_long_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(data[3:-3], rv["value"])
        
        data="'''another long string'''"
        self.s.merge(data, "literal_sq_long_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(data[3:-3], rv["value"])
        
        data="'an escaped \\' short string'"
        output="an escaped ' short string"
        self.s.merge(data, "literal_sq_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(output, rv["value"])
                
        data="''"
        output=""
        self.s.merge(data, "literal_sq_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(output, rv["value"])
        
        data="'\n'"
        output="\n"
        self.s.merge(data, "literal_sq_string_data")
        rv=literals.l_string(self.s, self.log)
        
        self.assertNotEqual(None, rv)
        self.assertEqual(output, rv["value"])
        