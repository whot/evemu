import unittest

from evemu.device import EvEmuDevice
from evemu.testing import BaseTestCase


class EvEmuDeviceTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuDeviceTestCase, self).setUp()
        self.device = EvEmuDevice(self.library, self.device_name)

    def test_initialize(self):
        self.assertTrue(self.device._device, self.device_name)


if __name__ == "__main__":
    unittest.main()
