import ctypes
import unittest

from evemu import util
from evemu.device import EvEmuDevice
from evemu.testing import skip, BaseTestCase


class EvEmuDeviceTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuDeviceTestCase, self).setUp()
        self.device = None

    def create_testing_device(self):
        """
        This is a conveneince test function for tests that need a device. Have
        this method be called in each test (as opposed to once in the setUp
        method) also allows for use to check device counts before and after
        device creation.
        """
        self.device = EvEmuDevice(self.library)
        self.device.create_node(self.get_device_file())

    def tearDown(self):
        print "preparing to tear down..."
        if self.device:
            # XXX this is where the bomb happens...
            self.device.destroy()
        print "preparing to upcall tearDown..."
        super(EvEmuDeviceTestCase, self).tearDown()
        print "finished tear-down."

    def test_new(self):
        pass

    def test_initialize_error_new(self):
        pass

    def test_initialize(self):
        self.assertTrue(self.device._device_pointer is not None)

    def test_get_lib(self):
        lib = self.device.get_lib()
        self.assertTrue(lib is not None)

    def test_get_device_pointer(self):
        pointer = self.device.get_device_pointer()
        self.assertEqual(type(pointer), int)

    def test_read(self):
        pass

    def test_create_node(self):
        device_count_before = len(util.get_all_device_numbers())
        self.create_testing_device()
        device_count_after = len(util.get_all_device_numbers())
        self.assertEqual(device_count_before + 1, device_count_after)

    @skip("Not ready yet")
    def test_version(self):
        import pdb;pdb.set_trace()
        self.assertEqual(self.device.version, "XX")

    @skip("Not ready yet")
    def test_name(self):
        self.assertEqual(self.device.name, "XX")


if __name__ == "__main__":
    unittest.main()
