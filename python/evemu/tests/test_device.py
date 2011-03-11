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

if __name__ == "__main__":
    unittest.main()
