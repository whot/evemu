from ctypes.util import find_library
import os
import unittest

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
            standardMsg = '%s not found in %s' % (repr(member),
                                                  repr(container))
            self.fail(msg or standardMsg)


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
        basedir = util.get_top_directory()
        self.data_dir = os.path.join(basedir, "..", "..", "data")
        self.device = None

    def get_device_file(self):
        return os.path.join(self.data_dir, "ntrig-dell-xt2.prop")

    def get_events_file(self):
        return os.path.join(self.data_dir, "ntrig-dell-xt2.event")

    def create_testing_device(self, device_class=None):
        """
        This is a conveneince test function for tests that need a device. Have
        this method be called in each test (as opposed to once in the setUp
        method) also allows for use to check device counts before and after
        device creation.
        """
        from evemu.device import EvEmuDevice
        if not device_class:
            device_class = EvEmuDevice
        self.device = device_class(self.library)
        self.device.create_node(self.get_device_file())
