from ctypes.util import find_library
from datetime import datetime
import os
import unittest

from evemu import const
from evemu import util


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        library = find_library(const.LIB)
        if not library:
            if os.path.exists(const.DEFAULT_LIB):
                library = const.DEFAULT_LIB
            else:
                library = const.LOCAL_LIB
        self.library = library
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.device_name = "evm tst dvc: %s" % timestamp
        basedir = util.get_test_directory()
        self.data_dir = os.path.join(basedir, "data", "ntrig-xt2")

    def get_device_file(self):
        return os.path.join(self.data_dir, "ntrig-xt2.device")

    def get_events_file(self):
        return os.path.join(self.data_dir, "ntrig-xt2-4-tap.event")


class CustomTestResult(unittest.TextTestResult):

    def __init__(self, *args, **kwds):
        super(CustomTestResult, self).__init__(*args, **kwds)
        self.current_module_and_class = ""
        self.last_module_and_class = ""

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        if not self.showAll:
            return
        self.last_module_and_class = self.current_module_and_class
        method = test._testMethodName
        module_and_class = test.id().rsplit(method)[0][:-1]
        self.current_module_and_class = module_and_class
        if self.last_module_and_class != self.current_module_and_class:
            heading = "\n%s.%s" % (util.get_test_module(), module_and_class)
            self.stream.writeln(heading)
        self.stream.write("\t%s " % method.ljust(50, "."))
        self.stream.write(" ")
        self.stream.flush()


def runTests():
    loader = unittest.TestLoader()
    suite = loader.discover(util.get_test_directory())
    runner = unittest.TextTestRunner(verbosity=2, resultclass=CustomTestResult)
    runner.run(suite)


if __name__ == "__main__":
    runTests()
