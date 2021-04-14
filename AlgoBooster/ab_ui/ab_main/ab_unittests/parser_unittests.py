import unittest
from ..ps2py_parser import ps2py_yacc as ycc


class TestAssignment(unittest.TestCase):
    """ Class for testing assignments. """

    def test_assignment(self):
        """ Tests 'normal' assignments without calculations.

        Keyword arguments:
        self -- the TestAssignment instance
        """
        statement = "a <- 3"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = 3')
        
        statement = "a <- {1, 2, 3}"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = {1,2,3}')

        statement = "a <- [1, 2, 3]"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = [1,2,3]')

        statement = "a[1] <- 3"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a[1] = 3')

        statement = "a <- b[3]"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = b[3]')

        statement = "a <- func(b)"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = func(b)')

        statement = "a <- func(b, c)"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = func(b, c)')

    def test_calcAssignment(self):
        """ Tests assignments containing a calculation.

        Keyword arguments:
        self -- the TestAssignment instance
        """
        statement = "a <- 3 + b"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = 3 + b')

        statement = "a <- 9//3"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = 9 // 3')

        statement = "a <- 9^3 * (9%3)"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = 9 ** 3 * (9 % 3)')

        statement = "a <- b[3] + c[2]"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'a = b[3] + c[2]')

class TestConditions(unittest.TestCase):
    """ Class for testing conditions. """

    def test_ifcond(self):
        """ Tests if-conditions.

        Keyword arguments:
        self -- the TestConditions instance
        """
        statement = "if a then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a:\n\tb = 3')

        statement = "if a<3 then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a < 3:\n\tb = 3')

        statement = "if a<=3 then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a <= 3:\n\tb = 3')

        statement = "if a>3 or not a != c then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a > 3 or not(a != c):\n\tb = 3')

        statement = "if a>=3 and (c ==1) then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a >= 3 and (c == 1):\n\tb = 3')

        statement = "if a < b then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a < b:\n\tb = 3')

        statement = "if a < b and not d then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a < b and not(d):\n\tb = 3')

        statement = "if (a) then b <- 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if (a):\n\tb = 3')

        statement = "if a then b <- 3\na <- 9 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a:\n\tb = 3\n\ta = 9')

    def test_ifelsecond(self):
        """ Tests if-else-conditions.

        Keyword arguments:
        self -- the TestConditions instance
        """
        statement = "if a < b and (a > 1) then b <- 3 else c <- 1+ 3 endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a < b and (a > 1):\n\tb = 3\nelse:\n\tc = 1 + 3')

    def test_ifcondnested(self):
        """ Tests nested if-conditions.

        Keyword arguments:
        self -- the TestConditions instance
        """
        statement = "if a < b and not d then if c then e <- 3 endif endif"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'if a < b and not(d):\n\tif c:\n\t\te = 3')

class TestLoops(unittest.TestCase):
    """ Class for testing loops. """

    def test_repeatWhile(self):
        """ Tests repeat-while-loops.

        Keyword arguments:
        self -- the TestLoops instance
        """
        statement = "repeat a <- 3 until a < 100"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'while True:\n\ta = 3\n\tif a < 100:\n\t\tbreak')


    def test_forRange(self):
        """ Tests for-loops with ranges.

        Keyword arguments:
        self -- the TestLoops instance
        """
        statement = "for i in 1 to 10 by 1 do a <- 10+i endfor"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'for i in range(1,10,1):\n\ta = 10 + i')


    def test_forIn(self):
        """ Tests for-loops with the 'in' keyword.

        Keyword arguments:
        self -- the TestLoops instance
        """
        statement = "for i in menge do a <- 10 endfor"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'for i in menge:\n\ta = 10')

        statement = "for i in menge do if a < 3 then a <- 3 endif endfor"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'for i in menge:\n\tif a < 3:\n\t\ta = 3')

class TestProcs(unittest.TestCase):
    """ Class for testing procedures. """

    def test_noReturn(self):
        """ Tests procedures without return statement.

        Keyword arguments:
        self -- the TestProcs instance
        """
        statement = "procedure func (param1, param2) a <- 3 endproc"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'def func (param1,param2):\n\ta = 3')

    
    def test_withReturn(self):
        """ Tests procedures with return statement(s).

        Keyword arguments:
        self -- the TestProcs instance
        """
        statement = "procedure func (param1) a <- 3 return endproc"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'def func (param1):\n\ta = 3\n\treturn')

        statement = "procedure func (param1, param2) return param2 endproc"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'def func (param1,param2):\n\treturn param2')

        statement = "procedure func (param1, param2) if param1 > param2 then return param2 else return param1 endif endproc"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'def func (param1,param2):\n\tif param1 > param2:\n\t\treturn param2\n\telse:\n\t\treturn param1')

    def test_complexProc(self):
        """ Tests complex procedures.

        Keyword arguments:
        self -- the TestProcs instance
        """
        statement = "procedure func (param1, param2) repeat a <- 3 + {1,2,3} until a == 100 return param2 endproc"
        self.assertEqual(ycc.parse_ps2py(statement).get('errors'), "")
        self.assertEqual(ycc.parse_ps2py(statement).get('result'), 'def func (param1,param2):\n\twhile True:\n\t\ta = 3 + {1,2,3}\n\t\tif a == 100:\n\t\t\tbreak\n\treturn param2')


# called by
# python -m ab_ui.ab_main.ab_unittests.parser_unittests
if __name__ == '__main__':
    
    unittest.main()    
    