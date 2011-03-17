import ctypes
import unittest

from evemu import exception
from evemu import util
from evemu.device import EvEmuDevice
from evemu.testing import testcase


class EvEmuDeviceTestCase(testcase.BaseTestCase):

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
        if self.device:
            self.device.destroy()
        super(EvEmuDeviceTestCase, self).tearDown()

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

    # XXX finish unit test
    def test_read(self):
        pass

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
        device = FakeDevice(self.library)
        self.assertRaises(
            exception.EvEmuError, 
            device.create_node, 
            self.get_device_file())

    def test_create_node_error_create(self):
        class FakeDevice(EvEmuDevice):
            def _create(self, *args, **kwds):
                raise exception.EvEmuError("Error calling lib in _create")
            def _open_uinput(self, *args, **kwds):
                pass
            def _new(self):
                pass
            def read(self, *args):
                pass
            def close(self):
                pass
        device = FakeDevice(self.library)
        self.assertRaises(
            exception.EvEmuError, 
            device.create_node, 
            self.get_device_file())

    def test_create_node(self):
        device_count_before = len(util.get_all_device_numbers())
        self.create_testing_device()
        device_count_after = len(util.get_all_device_numbers())
        self.assertEqual(device_count_before + 1, device_count_after)

    def test_version(self):
        self.create_testing_device()
        self.assertEqual(self.device.version, 0)

    def test_name(self):
        self.create_testing_device()
        self.assertEqual(self.device.name, "N-Trig-MultiTouch-Virtual-Device")

    def test_id_bustype(self):
        self.create_testing_device()
        self.assertEqual(self.device.id_bustype, 3)

    def test_id_vendor(self):
        self.create_testing_device()
        self.assertEqual(self.device.id_vendor, "0x1b96")

    def test_id_product(self):
        self.create_testing_device()
        self.assertEqual(self.device.id_product, 1)

    def test_id_version(self):
        self.create_testing_device()
        self.assertEqual(self.device.id_version, 272)

    def test_get_abs_minimum(self):
        self.create_testing_device()
        for event_code in xrange(10):
            self.assertEqual(self.device.get_abs_minimum(event_code), 0)

    def test_get_abs_maximum(self):
        self.create_testing_device()
        event_code = 0
        self.assertEqual(self.device.get_abs_maximum(event_code), 9600)

    def test_get_abs_fuzz(self):
        self.create_testing_device()
        event_code = 0
        self.assertEqual(self.device.get_abs_fuzz(event_code), 75)

    def test_get_abs_flat(self):
        self.create_testing_device()
        event_code = 0
        self.assertEqual(self.device.get_abs_flat(event_code), 0)

    def test_get_abs_resolution(self):
        self.create_testing_device()
        event_code = 0
        self.assertEqual(self.device.get_abs_resolution(event_code), 0)

    def test_has_prop(self):
        self.create_testing_device()
        event_code = 0
        self.assertEqual(self.device.has_prop(event_code), 0)

    def test_has_event(self):
        self.create_testing_device()
        event_type = 0
        event_code = 0
        self.assertEqual(self.device.has_event(event_type, event_code), 1)


if __name__ == "__main__":
    unittest.main()
