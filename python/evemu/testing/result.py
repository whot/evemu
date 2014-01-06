import unittest

import evemu.tests


try:
    # Python 2.7
    from unittest import TextTestResult
except ImportError:
    # Python 2.4, 2.5, 2.6
    from unittest import _TextTestResult as TextTestResult


def get_test_directory():
    return evemu.tests.__path__[0]


def get_test_module():
    return get_test_directory().replace("/", ".")


class CustomTestResult(TextTestResult):

    def __init__(self, *args, **kwds):
        super(CustomTestResult, self).__init__(*args, **kwds)
        self.current_module = ""
        self.last_module = ""
        self.current_class = ""
        self.last_class = ""

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        if not self.showAll:
            return
        self.last_module = self.current_module
        self.last_class = self.current_class
        method = test._testMethodName
        module_and_class = test.id().rsplit(method)[0][:-1]
        this_module = ".".join(module_and_class.split(".")[:-1])
        self.current_module = this_module
        this_class = module_and_class.split(".")[-1]
        self.current_class = this_class
        if self.last_module != self.current_module:
            heading = "\n%s.%s" % (get_test_module(), this_module)
            self.stream.writeln(heading)
        if self.last_class != self.current_class:
            self.stream.writeln("    %s" % this_class)
        self.stream.write("        %s " % method.ljust(50, "."))
        self.stream.write(" ")
        self.stream.flush()

