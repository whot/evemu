import unittest

from evemu import util
from evemu.testing import skip, BaseTestCase
from evemu.wrapper import EvEmuWrapper


class EvEmuWrapperTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuWrapperTestCase, self).setUp()
        self.wrapper = EvEmuWrapper(self.library)

    def tearDown(self):
        if self.wrapper.device:
            self.wrapper.device.destroy()
        super(EvEmuWrapperTestCase, self).tearDown()

    def test_initialize(self):
        self.assertTrue(self.wrapper.device is not None)
        self.assertTrue(self.wrapper.get_device() is not None)

    def test_create_already_created(self):
        pass

    def test_create(self):
        self.wrapper.create(self.get_device_file())
        device_list = util.get_all_device_names()
        self.assertTrue("N-Trig-MultiTouch-Virtual-Device" in device_list)

    @skip("Not ready yet")
    def test_read(self):
        # XXX finish unit test
        result = self.wrapper.read(self.get_device_file())
        # XXX need to do checks against the result

    @skip("Not ready yet")
    def test_extract(self):
        # XXX finish unit test
        result = self.wrapper.extract(self.get_device_file())
        print "\nfilename: %s" % self.get_device_file()
        import os
        print "exists? %s" % str(os.path.exists(self.get_device_file()))
        print "result:\n%s" % result


if __name__ == "__main__":
    unittest.main()
