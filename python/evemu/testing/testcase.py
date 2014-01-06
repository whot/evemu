from ctypes.util import find_library
import os
import unittest

from evemu import const
from evemu import exception


def get_top_directory():
    import evemu
    return evemu.__path__[0]


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
        basedir = get_top_directory()
        self.data_dir = os.path.join(basedir, "..", "..", "data")
        self.device = None

    def tearDown(self):
       if self.device:
            self.device.destroy()
       super(BaseTestCase, self).tearDown()

    def get_device_file(self):
        return os.path.join(self.data_dir, "ntrig-dell-xt2.prop")

    def get_events_file(self):
        return os.path.join(self.data_dir, "ntrig-dell-xt2.event")

