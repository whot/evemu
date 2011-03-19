import ctypes
import tempfile
import unittest

from evemu import const
from evemu import exception
from evemu import util
from evemu.device import EvEmuDevice
from evemu.testing import testcase


class EvEmuDeviceTestCase(testcase.BaseTestCase):

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

    def test_write(self):
        import os
        self.create_testing_device()
        (output_fd, filename) = tempfile.mkstemp()
        self.device.write(filename)
        import pdb;pdb.set_trace()
        os.close(output_fd)
        import pdb;pdb.set_trace()
        data = open(filename).read()
        self.assertEqual(data, "XX")


class EvEmuDevicePropertyTestCase(testcase.BaseTestCase):

    def get_ev_abs_codes(self):
        return const.absolute_axes.values()

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
        self.assertEqual(hex(self.device.id_vendor), "0x1b96")

    def test_id_product(self):
        self.create_testing_device()
        self.assertEqual(self.device.id_product, 1)

    def test_id_version(self):
        self.create_testing_device()
        self.assertEqual(self.device.id_version, 272)


class EvEmuDeviceGetterTestCase(testcase.BaseTestCase):

    def test_get_abs_minimum(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self.device.get_abs_minimum(x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_get_abs_maximum(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9600, 7200, 0, 0, 0, 0,
            7200, 1, 7200, 0, 9600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9600,
            0, 0,
            ]
        # Skipping the entry for ABS_CNT; some times it's 0, sometimes a very
        # large negative number.
        results = [self.device.get_abs_maximum(x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results[:-1], expected[:-1])

    def test_get_abs_fuzz(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 75, 78, 0, 0, 0, 0, 150,
            0, 78, 0, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200, 0, 0, 
            ]
        results = [self.device.get_abs_fuzz(x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_get_abs_flat(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self.device.get_abs_flat(x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_get_abs_resolution(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self.device.get_abs_resolution(x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_has_prop(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self.device.has_prop(x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_has_event_ev_abs(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1,
            1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
            ]
        results = [self.device.has_event(const.event_types["EV_ABS"], x) 
                   for x in const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_has_event_ev_key(self):
        self.create_testing_device()
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self.device.has_event(const.event_types["EV_KEY"], x) 
                   for x in const.buttons.values()]
        self.assertEqual(results, expected)


if __name__ == "__main__":
    unittest.main()
