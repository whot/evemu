import os
import unittest

import evemu.exception
from evemu import event_get_name, event_get_value, input_prop_get_value, input_prop_get_name

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
                    raise evemu.exception.SkipTest(message)
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

    _expected_abs_ntrig_dell_xt2 = {
            # A: 00 0 9600 75 0 0
            evemu.event_get_value("EV_ABS", "ABS_X"):
                {"min": 0, "max": 9600, "fuzz": 75, "flat": 0, "res": 0},
            # A: 01 0 7200 78 0 0
            evemu.event_get_value("EV_ABS", "ABS_Y"):
                {"min": 0, "max": 7200, "fuzz": 78, "flat": 0, "res": 0},
            # A: 30 0 9600 200 0 0
            evemu.event_get_value("EV_ABS", "ABS_MT_TOUCH_MAJOR"):
                {"min": 0, "max": 9600, "fuzz": 200, "flat": 0, "res": 0},
            # A: 31 0 7200 150 0 0
            evemu.event_get_value("EV_ABS", "ABS_MT_TOUCH_MINOR"):
                {"min": 0, "max": 7200, "fuzz": 150, "flat": 0, "res": 0},
            # A: 34 0 1 0 0 0
            evemu.event_get_value("EV_ABS", "ABS_MT_ORIENTATION"):
                {"min": 0, "max": 1, "fuzz": 0, "flat": 0, "res": 0},
            # A: 35 0 9600 75 0 0
            evemu.event_get_value("EV_ABS", "ABS_MT_POSITION_X"):
                {"min": 0, "max": 9600, "fuzz": 75, "flat": 0, "res": 0},
            # A: 36 0 7200 78 0 0
            evemu.event_get_value("EV_ABS", "ABS_MT_POSITION_Y"):
                {"min": 0, "max": 7200, "fuzz": 78,  "flat": 0, "res": 0}
            }
    _expected_key_ntrig_dell_xt2 = {
            evemu.event_get_value("EV_KEY", "BTN_TOUCH"): True
            }

    def get_expected_abs(self, sub_key):
        expected_items = self._expected_abs_ntrig_dell_xt2.items()

        absmax = event_get_value("EV_ABS", "ABS_MAX")
        expected = dict.fromkeys(range(0, absmax + 1), 0)
        expected.update((k, v[sub_key]) for (k, v) in expected_items)

        return expected

    def get_expected_absbits(self):
        expected_keys = self._expected_abs_ntrig_dell_xt2.keys()

        absmax = event_get_value("EV_ABS", "ABS_MAX")
        expected = dict.fromkeys(range(0, absmax + 1), False)
        expected.update((k, True) for k in expected_keys)

        return expected

    def get_expected_keybits(self):
        expected_keys = self._expected_key_ntrig_dell_xt2.keys()
        keymax = event_get_value("EV_KEY", "KEY_MAX")
        expected = dict.fromkeys(range(0, keymax + 1), False)
        expected.update((k, True) for k in expected_keys)

        return expected

    def get_expected_propbits(self):
        # no props for N-Trig-MultiTouch-Virtual-Device, so we
        # return a dict with all keys on False
        propmax = input_prop_get_value("INPUT_PROP_MAX")
        keys = range(0, propmax + 1)
        return dict.fromkeys(keys, False)
