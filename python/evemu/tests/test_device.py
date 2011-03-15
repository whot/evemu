import ctypes
import unittest

from evemu import exception
from evemu import util
from evemu.device import EvEmuDevice
from evemu.testing import skip, BaseTestCase


class EvEmuDeviceTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuDeviceTestCase, self).setUp()
        self.device = None

    def create_testing_device(self, device_class=None):
        """
        This is a conveneince test function for tests that need a device. Have
        this method be called in each test (as opposed to once in the setUp
        method) also allows for use to check device counts before and after
        device creation.
        """
        if not device_class:
            device_class = EvEmuDevice
        self.device = device_class(self.library)
        self.device.create_node(self.get_device_file())

    def tearDown(self):
        print "preparing to tear down..."
        if self.device:
            # XXX this is where the bomb happens...
            self.device.destroy()
            pass
        print "preparing to upcall tearDown..."
        super(EvEmuDeviceTestCase, self).tearDown()
        print "finished tear-down."

    def test_new(self):
        pass

    def test_initialize_error_new(self):
        class FakeDevice(EvEmuDevice):
            def _new(self):
                raise exception.EvEmuError("Error new'ing in init!")
        self.assertRaises(
            exception.EvEmuError, self.create_testing_device, FakeDevice)

    def test_initialize(self):
        self.create_testing_device()
        self.assertTrue(self.device._device_pointer is not None)

    def test_get_lib(self):
        self.create_testing_device()
        lib = self.device.get_lib()
        self.assertTrue(lib is not None)

    def test_get_device_pointer(self):
        self.create_testing_device()
        pointer = self.device.get_device_pointer()
        self.assertEqual(type(pointer), int)

    def test_read_error(self):
        class FakeDevice(EvEmuDevice):
            def _read(self, *args, **kwds):
                raise exception.EvEmuError("Error calling lib in _read")
            def create_node(self, *args):
                pass
        self.create_testing_device(FakeDevice)
        self.assertRaises(
            exception.EvEmuError, self.device.read, self.get_device_file())

    def test_read(self):
        pass

    # XXX the following test is causing a double free memory error
    def test_create_node_error_uinput(self):
        class FakeDevice(EvEmuDevice):
            def _open_uinput(self, *args, **kwds):
                raise exception.EvEmuError("Error calling lib in _uinput")
            def _new(self):
                pass
            def read(self, *args):
                pass
            def delete(self):
                pass
            def destory(self):
                pass
            def close(self):
                pass
        device = FakeDevice(self.library)
        self.assertRaises(
            ValueError,
            #exception.EvEmuError, 
            device.create_node, 
            self.get_device_file())

    def test_create_node_error_create(self):
        class FakeDevice(EvEmuDevice):
            def _read(self, *args, **kwds):
                raise exception.EvEmuError("Error calling lib in _create")

    def test_create_node(self):
        device_count_before = len(util.get_all_device_numbers())
        self.create_testing_device()
        device_count_after = len(util.get_all_device_numbers())
        self.assertEqual(device_count_before + 1, device_count_after)

    @skip("Not ready yet")
    def test_version(self):
        self.assertEqual(self.device.version, "XX")

    @skip("Not ready yet")
    def test_name(self):
        self.assertEqual(self.device.name, "XX")


if __name__ == "__main__":
    unittest.main()
