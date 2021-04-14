
import unittest
from .. import ast_extraction 

class TestAttrClasses():
    """ Parent test class for preparation of the attribute extraction test """


    def prepare(self, code, attr_name):
        """ Does the attribute extraction and returns only the needed attribute.

		Keyword arguments:
		self -- the TestAttrClasses instance
        code -- the code for the attribute extraction in Python
        attr_name -- the name of the attribute to test
        """

        extraction = ast_extraction.AttributeFinder("", True)
        root = extraction.parseCodeToAST(code)
        attrs = extraction.extractAttributes(root)
        if root is None or attrs == "":
            raise("No attribute extracted.")
        
        # extract fitting attribute
        try:
            search_attr = attrs.get(attr_name)
        except IndexError as ie:
            print(ie)
            raise("No attribute extracted.")

        if search_attr is None:
            raise("No attribute extracted.")

        return search_attr

class TestRecCount(unittest.TestCase, TestAttrClasses):
    """ Test class for RecCount """

    attr_name = "RecCount"

    def test_noRec(self):
        """ Tests the correct results for codes without recursion.

        Keyword arguments:
        self -- the TestRecCount instance
        """
        
        code = """
a = 3
b = a/1
c = b
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
for i in range(0, 10):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        
    def test_oneRec(self):
        """ Tests the correct results for codes with one recursion.

        Keyword arguments:
        self -- the TestRecCount instance
        """
        code = """
def func(a, b):
    if a < 0:
        return a
    return func(a-b, b)

func(5, 2)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
def func(a, b):
    if a > 0:
        return func(a-b, b)
    return a

func(5, 2)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)


    def test_twoRecs(self):
        """ Tests the correct results for codes with two recursive calls in the same function.

        Keyword arguments:
        self -- the TestRecCount instance
        """

        code = """
def func(a, b):
    if a < 0:
        return a 
    return func(a-b, b) - func(a, b)
    
func(5, 2)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

        code = """
def func(a, b):
    if a < 0:
        return a 
    return func(a-b, b) 
    return func(a, b)
    
func(5, 2)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

    def test_threeRecs(self):
        """ Tests the correct results for codes with three recursive calls in the same function.

        Keyword arguments:
        self -- the TestRecCount instance
        """

        code = """
def func(a, b):
    if a < 0:
        return a 
    return func(a-b, b) - func(a-b, b) - func(a-b, b)
    
func(5, 2)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 3)

class TestLoopNDepend(unittest.TestCase, TestAttrClasses):
    """ Test class for LoopNDepend """

    attr_name = "LoopNDepend"

    def test_notNDepend(self):
        """ Tests the correct results for codes with no n depend loop.

        Keyword arguments:
        self -- the TestLoopNDepend instance
        """

        code = """
for i in range(0,10,1):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
i = 0
while True:
    i = i+1
    if i < 10:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)


    def test_nDepend(self):
        """ Tests the correct results for codes with at least one n depend loop.

        Keyword arguments:
        self -- the TestLoopNDepend instance
        """
        code = """
menge = { }
for i in menge:
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
a = [1, 2, 3]
i = 0
while True:
    if a[i] > 2:
        break
    i = i+1
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)
        

class TestLoopNested(unittest.TestCase, TestAttrClasses):
    """ Test class for LoopNested """

    attr_name = "LoopNested"

    def test_noLoop(self):
        """ Tests the correct results for codes with no loop.

        Keyword arguments:
        self -- the TestLoopNested instance
        """

        code = """
a = 3
b = a/3
c = 9
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
def func(a, b):
    return a-b

func(9, 10)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

    def test_oneNested(self):
        """ Tests the correct results for codes with at least one loop (not nested).

        Keyword arguments:
        self -- the TestLoopNested instance
        """

        code = """
for i in range(1, 10, 1):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
for i in range(1, 10, 1):
    a = i

for j in range(2, 11, 2):
    a = j
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
i = 0
while True:
    a = i
    i += 1
    if i < 10:
        break

for j in range(2, 11, 2):
    a = j
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

    def test_twoNested(self):
        """ Tests the correct results for codes with once-nested loops.

        Keyword arguments:
        self -- the TestLoopNested instance
        """

        code = """
for i in range(1, 10, 1):
    a = i
    for j in range(2, 11, 2):
        a = j
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

        code = """
for i in range(1, 10, 1):
    a = i
    j = 0
    while True:
        a = j
        j += 1
        if j < 9:
            break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

        code = """
j = 0
while True:
    a = j
    j += 1
    for i in range(1, 10, 1):
        a = i
    if j < 9:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

        code = """
j = 0
while True:
    a = j
    j += 1
    for i in range(1, 10, 1):
        a = i
    if j < 9:
        break

k = 9
while True:
    a = k
    k += 1
    if j < 11:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

    def test_threeNested(self):
        """ Tests the correct results for codes with twice-nested loops.

        Keyword arguments:
        self -- the TestLoopNested instance
        """
        code = """
j = 0
while True:
    a = j
    j += 1
    for i in range(1, 10, 1):
        a = i
        k = 9
        while True:
            a = k
            k += 1
            if k < 11:
                break
    if j < 9:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 3)

        code = """
j = 0
while True:
    a = j
    j += 1
    for i in range(1, 10, 1):
        a = i
        for c in range(10, 8, -1):
            a = c
    if j < 9:
        break
k = 9
while True:
    a = k
    k += 1
    if k < 11:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 3)

    def test_fourNested(self):
        """ Tests the correct results for codes with three-times-nested loops.

        Keyword arguments:
        self -- the TestLoopNested instance
        """
        code = """
j = 0
while True:
    a = j
    j += 1
    for i in range(1, 10, 1):
        a = i
        for c in range(10, 8, -1):
            a = c
            k = 9  
            while True:
                a = k
                k += 1
                if k < 11:
                    break
    if j < 9:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 4)

class TestLoopType(unittest.TestCase, TestAttrClasses):
    """ Test class for LoopType """

    attr_name = "LoopType"

    def test_noLoop(self):
        """ Tests the correct results for codes without loop.

        Keyword arguments:
        self -- the TestLoopType instance
        """
        code = """
def func(a, b):
    return a+b
func(1,2)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
a = 3
b = a
c = a-b
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

    def test_forLoop(self):
        """ Tests the correct results for codes with at least one for-loop, but no while-loop.

        Keyword arguments:
        self -- the TestLoopType instance
        """
        code = """
for i in range(1, 10, 1):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
menge = { }
for i in menge:
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

    def test_whileLoop(self):
        """ Tests the correct results for codes with at least one while-loop.

        Keyword arguments:
        self -- the TestLoopType instance
        """
        code = """
i = 0
while True:
    a = i
    i += 1
    if i < 9:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

        code = """
menge = { }
for i in menge:
    a = i

i = 0
while True:
    a = i
    i += 1
    if i < 9:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 2)

class TestProgTerminate(unittest.TestCase, TestAttrClasses):
    """ Test class for ProgTerminate """

    attr_name = "ProgTerminate"

    def test_term(self):
        """ Tests the correct results for codes which terminate normally.

        Keyword arguments:
        self -- the TestProgTerminate instance
        """

        code = """
menge = { }
for i in menge:
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
i = 0
while True:
    a = i
    i += 1
    if i < 10:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
def func(a):
    if a < 3:
        return a
    return func(a-3)

func(9)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

    def test_notTerm(self):
        """ Tests the correct results for codes which do not terminate normally.

        Keyword arguments:
        self -- the TestProgTerminate instance
        """
        code = """
def func(a):
    return func(a-3)

func(9)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
while True:
    a = 3
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
while True:
    a = i
    if i < 10:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

class TestUsingNonScalar(unittest.TestCase, TestAttrClasses):
    """ Test class for UsingNonScalar """

    attr_name = "UsingNonScalar"

    def test_noNonScalar(self):
        """ Tests the correct results for codes which do not use non scalars.

        Keyword arguments:
        self -- the TestUsingNonScalar instance
        """
        code = """
for i in range(1, 10, 1):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
i = 0
while True:
    a = i
    i += 1
    if i < 10:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
def func(a):
    if a < 3:
        return a
    return func(a-3)
func (3)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

    def test_nonScalar(self):
        """ Tests the correct results for codes which use non scalars.

        Keyword arguments:
        self -- the TestUsingNonScalar instance
        """
        code = """
menge = { 1, 2, 3}
for i in menge:
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
liste = [ 1, 2, 3]
for i in menge:
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

class TestRepeatValues(unittest.TestCase, TestAttrClasses):
    """ Test class for RepeatValues """

    attr_name = "RepeatValues"

    def test_noRepeatValues(self):
        """ Tests the correct results for codes which do not have repeating values.

        Keyword arguments:
        self -- the TestRepeatValues instance
        """

        code = """
a = 0
for i in range(1, 10, 1):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

    def test_repeatValues(self):
        """ Tests the correct results for codes which have repeating values.

        Keyword arguments:
        self -- the TestRepeatValues instance
        """
        code = """
a = 2
for i in range(1, 10, 1):
    if i % a == 0:
        a = 2
    else:
        a = 2
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
i = 0
while True:
    a = i % 2
    i += 1
    if i > 10:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
def func(a, b):
    a = 10 % b
    if b > 1:
        func(a, b-1)
func(10, 7)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)
    
class TestReuseValues(unittest.TestCase, TestAttrClasses):
    """ Test class for Reuse Values """

    attr_name = "ReuseValues"

    def test_noReuseValues(self):
        """ Tests the correct results for codes which do not reuse values.

        Keyword arguments:
        self -- the TestReuseValues instance
        """
        code = """
a = 9
b = 3
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)
        
        code = """
a = 9
for b in range(0, 10, 2):
    b = a
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
a = 9
for b in range(0, a, 2):
    b = a
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

        code = """
a = 9
i = 1
while True:
    i += 1
    if i < 3:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 0)

    def test_reuseValues(self):
        """ Tests the correct results for codes which reuse values.

        Keyword arguments:
        self -- the TestReuseValues instance
        """
        code = """
i = 0
while True:
    a = i-1
    if i < 9:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
i = 0
for j in range(0, 7, 1):
    a = i-j
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)

        code = """
def func(a, b):
    a = b-1
    return func(a, b-1)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, 1)


class TestgetComplexity(unittest.TestCase, TestAttrClasses):
    """ Test for getComplexity method """

    attr_name = "Complexity"

    def test_constant(self):
        """ Tests the correct results for codes which have the complexity O(c).

        Keyword arguments:
        self -- the TestgetComplexity instance
        """
        code = """
a = 3
b = 2
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "0")

    def test_log(self):
        """ Tests the correct results for codes which have the complexity O(log(n)).

        Keyword arguments:
        self -- the TestgetComplexity instance
        """
        code = """
i = 10
while True:
    i = i / 2
    if i < 5:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "1")


    def test_linear(self):
        """ Tests the correct results for codes which have the complexity O(n).

        Keyword arguments:
        self -- the TestgetComplexity instance
        """
        
        code = """
for i in range(1, 10, 1):
    a = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "2")

        code = """
a = [1, 2, 3]
i = 0
while True:
    if a[i] > 2:
        break
    i = i+1
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "2")

    
    def test_polynom(self):
        """ Tests the correct results for codes which have the complexity O(n^c).

        Keyword arguments:
        self -- the TestgetComplexity instance
        """
        code = """
for i in range(1, 10, 1):
    a = i
    for j in range(2, 11, 2):
        a = j
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "3")

        code = """
def func(a):
    if a == 1:
        return a
    return func(a/3)

func(3)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "3")

        code = """
a = [1,2,3]
for i in range(0,10,1):
    for j in range(0,10,1):
        a = a + [i]
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "3")



    def test_expon(self):
        """ Tests the correct results for codes which have the complexity O(c^n).

        Keyword arguments:
        self -- the TestgetComplexity instance
        """
        code = """
def func(a):
    if a > 3:
        return a
    return func(a-1)

func(-3)
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")

        code = """
a = {1, 2, 3}
for i in a:
    j = i
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")

        code = """
i = 0
while True:
    i = i+1
    if i < 10:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")

        code = """
i = 0
while True:
    i = i+1
    if i < 10:
        break
i = i / 10
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")

        code = """
for i in range(1, 10, 1):
    a = i
    j = 0
    while True:
        a = j
        j += 1
        if j < 9:
            break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")

        code = """
a = {1, 2, 3}
i = 0
while True:
    b = a[i]
    if i < 2:
        i = i - 1
    else:
        i = i + 1
    if i < 3:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")

        code = """
j = 0
while True:
    a = j
    j += 1
    for i in range(1, 10, 1):
        a = i
    if j < 9:
        break

k = 9
while True:
    a = k
    k += 1
    if k < 11:
        break
        """
        attr = self.prepare(code, self.attr_name)
        self.assertEqual(attr, "4")


# called by
# python -m ab_ui.ab_main.ab_unittests.test_extraction
if __name__ == '__main__':
    
    unittest.main()    
    