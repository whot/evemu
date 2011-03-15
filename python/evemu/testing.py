from ctypes.util import find_library
from datetime import datetime
import os
import unittest
try:
    # Python 2.7
    from unittest import TextTestResult
except ImportError:
    # Python 2.4, 2.5, 2.6
    from unittest import _TextTestResult as TextTestResult

from evemu import const
from evemu import exception
from evemu import util


def skip(message):
    try:
        return unittest.skip(message)
    except AttributeError:
        def _skip(message):
            def decorator(test_item):
                def skip_wrapper(*args, **kwds):
                    raise exception.SkipTest(message)
                return skip_wrapper
            return decorator
        return _skip(message)


class Non26BaseTestCase(unittest.TestCase):
    """
    This is to provide methods that aren't in 2.6 and below, but are in 2.7 and
    above.
    """
    def __init__(self, *args, **kwds):
        super(Non26BaseTestCase, self).__init__(*args, **kwds)
        if not hasattr(unittest.TestCase, "assertIn"):
            self.assertIn = self._assertIn26

    def _assertIn26(self, member, container, msg=None):
        """Just like self.assertTrue(a in b), but with a nicer default message."""
        if member not in container:
            standardMsg = '%s not found in %s' % (safe_repr(member),
                                                  safe_repr(container))
            self.fail(_formatMessage(msg, standardMsg))


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        library = find_library(const.LIB)
        if not library:
            if os.path.exists(const.DEFAULT_LIB):
                library = const.DEFAULT_LIB
            else:
                library = const.LOCAL_LIB
        self.library = library
        #timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #self.device_name = "evm tst dvc: %s" % timestamp
        #self.device_name = "evemu-%d:%s" % (os.getpid(), self._testMethodName)
        basedir = util.get_top_directory()
        self.data_dir = os.path.join(basedir, "..", "..", "data")

    def get_device_file(self):
        return os.path.join(self.data_dir, "ntrig-dell-xt2.prop")

    def get_events_file(self):
        return os.path.join(self.data_dir, "ntrig-dell-xt2.event")


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
            heading = "\n%s.%s" % (util.get_test_module(), this_module)
            self.stream.writeln(heading)
        if self.last_class != self.current_class:
            self.stream.writeln("    %s" % this_class)
        self.stream.write("        %s " % method.ljust(50, "."))
        self.stream.write(" ")
        self.stream.flush()


class CustomTestRunner(unittest.TextTestRunner):
    """
    This is only needed for Python 2.6 and lower.
    """
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)


def get_suite(loader, top_level_directory):
    if hasattr(loader, "discover"):
        # Python 2.7
        suite = loader.discover(top_level_directory)
    else:
        # Python 2.4, 2.5, 2.6
        names = []
        def _path_to_module(path):
            # generate dotted names for file paths
            path = path.replace(".py", "")
            return path.replace("/", ".")

        # walk the directory
        for dirpath, dirnames, filenames in os.walk(top_level_directory):
            modules = [
                _path_to_module(os.path.join(dirpath, x)) for x in filenames 
                    if x.startswith("test_") and x.endswith(".py")]
            if not modules:
                continue
            names.extend(modules)
        suite = loader.loadTestsFromNames(names)
    return suite


def get_runner():
    try:
        # Python 2.7
        runner = unittest.TextTestRunner(
            verbosity=2, resultclass=CustomTestResult)
    except TypeError:
        # Python 2.4, 2.5, 2.6
        runner = CustomTestRunner(verbosity=2)
    return runner


def run_tests():
    loader = unittest.TestLoader()
    suite = get_suite(loader, util.get_test_directory())
    get_runner().run(suite)


if __name__ == "__main__":
    run_tests()
