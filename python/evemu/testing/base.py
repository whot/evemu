from ctypes.util import find_library
import os
import tempfile
import unittest

from evemu import const


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        library = find_library(const.LIB)
        if not library:
            if os.path.exists(const.DEFAULT_LIB):
                library = const.DEFAULT_LIB
            else:
                library = const.LOCAL_LIB
        self.library = library
        self.device_name = "My Special Device"
        from evemu import tests
        basedir = tests.__path__[0]
        self.data_dir = os.path.join(basedir, "data", "ntrig-xt2")

    def get_device_file(self):
        return os.path.join(self.data_dir, "ntrig-xt2.device")

    def get_events_file(self):
        return os.path.join(self.data_dir, "ntrig-xt2-4-tap.event")
