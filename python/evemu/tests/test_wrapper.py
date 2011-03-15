import unittest

from evemu import util
from evemu.testing import skip, BaseTestCase
from evemu.wrapper import EvEmuWrapper


class EvEmuWrapperTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuWrapperTestCase, self).setUp()
        self.wrapper = EvEmuWrapper(self.library)

    def test_initialize(self):
        self.assertTrue(self.wrapper.device is not None)
        self.assertTrue(self.wrapper.get_device() is not None)

    def test_create_already_created(self):
        pass

    def test_create(self):
        result = self.wrapper.create(self.get_device_file())
        device_list = util.lsinput()
        device_list2 = util.get_all_device_names()
        import pdb;pdb.set_trace()
        self.assertTrue("N-Trig-MultiTouch Virtual Device" in device_list)

    @skip("Not ready yet")
    def test_read(self):
        # hrm... not sure if I should be reading from the device file or
        # preping an empty file...
        result = self.wrapper.read(self.get_device_file())
        # XXX need to do checks against the result

    @skip("Not ready yet")
    def test_extract(self):
        result = self.wrapper.extract(self.get_device_file())
        print "\nfilename: %s" % self.get_device_file()
        import os
        print "exists? %s" % str(os.path.exists(self.get_device_file()))
        print "result:\n%s" % result


if __name__ == "__main__":
    unittest.main()
