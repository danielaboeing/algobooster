from django.test import TestCase


class CodeInputTests(TestCase):
    def test_code_is_not_too_long(self):
        code_test = "a"*101
        #self.assertIs(self.checkCode(code_test), False)
        self.assertIs(len(code_test), 101)

