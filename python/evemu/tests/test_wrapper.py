import unittest

from evemu.wrapper import EvEmuWrapper
from evemu.testing.base import BaseTestCase


class EvEmuWrapperTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuWrapperTestCase, self).setUp()
        self.wrapper = EvEmuWrapper(self.device_name, self.library)

    def test_initialize(self):
        self.assertTrue(self.wrapper._device is not None)

    def test_read(self):
        # hrm... not sure if I should be reading from the device file or
        # preping an empty file...
        #result = self.wrapper.read(self.get_device_file())
        # XXX need to do checks against the result
        pass

    # XXX fill this test in
    def test_create(self):
        pass

    def test_extract(self):
        result = self.wrapper.extract(self.get_device_file())
        print "\nfilename: %s" % self.get_device_file()
        print "exists? %s" % str(os.path.exists(self.get_device_file()))
        print "result:\n%s" % result


if __name__ == "__main__":
    unittest.main()
