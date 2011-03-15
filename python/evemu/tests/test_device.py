import ctypes
import unittest

from evemu.device import EvEmuDevice
from evemu.testing import skip, BaseTestCase


class EvEmuDeviceTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuDeviceTestCase, self).setUp()
        self.device = EvEmuDevice(self.library)
        self.device.create_node(self.get_device_file())

    def tearDown(self):
        del(self.device)

    def test_initialize(self):
        self.assertTrue(self.device._device is not None)

    def XXX_test_get_lib(self):
        lib = self.device.get_lib()
        self.assertTrue(lib is not None)

    def XXX_test_get_device_fd(self):
        fd = self.device.get_device_fd()
        self.assertEqual(type(fd), int)

    def XXX_test_read(self):
        pass

    def XXX_test_create_node(self):
        pass

    #@skip("Not ready yet")
    def XXX_test_version(self):
        import pdb;pdb.set_trace()
        self.assertEqual(self.device.version, "XX")

    #@skip("Not ready yet")
    def XXX_test_name(self):
        self.assertEqual(self.device.name, "XX")


if __name__ == "__main__":
    unittest.main()
