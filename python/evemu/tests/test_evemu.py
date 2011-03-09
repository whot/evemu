from ctypes.util import find_library
import os
import unittest

from evemu import LIB, EvEmu


# This needs to get updated with new versions of evemu
LOCAL_LIB = "../src/.libs/libutouch-evemu.so.1.0.0"
# This should also be examined every release of evemu
API = [
    "evemu_new",
    "evemu_extract",
    "evemu_write",
    "evemu_read",
    "evemu_create",
    "evemu_destroy",
    "evemu_delete",
    "evemu_write_event",
    "evemu_read_event",
    "evemu_record",
    "evemu_play"]


class EvEmuTestCase(unittest.TestCase):

    def setUp(self):
        library = find_library(LIB)
        if not library:
            library = LOCAL_LIB
        self.evemu = EvEmu(library=library)
        from evemu import tests
        basedir = tests.__path__[0]
        self.data_dir = os.path.join(basedir, "data")

    def _get_device_file(self):
        return os.path.join(self.data_dir, "device.prop")

    def _get_events_file(self):
        return os.path.join(self.data_dir, "gesture.events")

    def test_initialize(self):
        # Make sure that the library loads
        self.assertNotEqual(
            self.evemu._evemu._name.find("libutouch-evemu"), -1)
        # Make sure that the expected functions are present
        for function_name in API:
            function = getattr(self.evemu._evemu, function_name)
            self.assertTrue(function is not None)

    def test_describe(self):
        pass

    def test_create_device(self):
        # Load the device file
        pass

    def test_record(self):
        pass

    def test_play(self):
        # Load the device file
        pass


if __name__ == "__main__":
    unittest.main()
