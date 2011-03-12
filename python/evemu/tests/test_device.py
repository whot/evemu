import ctypes
import unittest

from evemu.device import EvEmuDevice
from evemu.testing import BaseTestCase


class EvEmuDeviceTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuDeviceTestCase, self).setUp()
        self.device = EvEmuDevice(self.device_name, ctypes.CDLL(self.library))

    def test_initialize(self):
        self.assertTrue(self.device._device is not None)

    def test_get_lib(self):
        lib = self.device.get_lib()
        self.assertTrue(lib is not None)

    def test_get_device_fd(self):
        fd = self.device.get_device_fd()
        self.assertEqual(type(fd), int)

    @unittest.skip("Not ready yet")
    def test_version(self):
        self.assertEqual(self.device.version, "XX")

    @unittest.skip("Not ready yet")
    def test_name(self):
        self.assertEqual(self.device.name, "XX")


if __name__ == "__main__":
    unittest.main()
