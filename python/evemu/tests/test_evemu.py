from ctypes.util import find_library
import os
import tempfile
import unittest

from evemu import (
    const, EvEmu, EvEmuBase, EvEmuDevice, EvEmuWrapper2, WrapperError)


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        library = find_library(const.LIB)
        if not library:
            if os.path.exists(const.DEFAULT_LIB):
                library = const.DEFAULT_LIB
            else:
                library = const.LOCAL_LIB
        self.library = library
        self.device_name = "My Special Device"
        from evemu import tests
        basedir = tests.__path__[0]
        self.data_dir = os.path.join(basedir, "data", "ntrig-xt2")

    def get_device_file(self):
        return os.path.join(self.data_dir, "ntrig-xt2.device")

    def get_events_file(self):
        return os.path.join(self.data_dir, "ntrig-xt2-4-tap.event")

    def test_initialize(self):
        wrapper = EvEmuBase(self.library)
        # Make sure that the library loads
        self.assertNotEqual(
            wrapper._lib._name.find("libutouch-evemu"), -1)
        # Make sure that the expected functions are present
        for function_name in const.API:
            function = getattr(wrapper._lib, function_name)
            self.assertTrue(function is not None)


class EvEmuDeviceTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuDeviceTestCase, self).setUp()
        self.device = EvEmuDevice(self.library, self.device_name)

    def test_initialize(self):
        self.assertTrue(self.device._device, self.device_name)


class EvEmuWrapperTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuWrapperTestCase, self).setUp()
        self.wrapper = EvEmuWrapper2(self.device_name, self.library)

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


class EvEmuTestCase(BaseTestCase):

    def setUp(self):
        super(EvEmuTestCase, self).setUp()
        self.evemu = EvEmu(library=self.library)

    def test_describe(self):
        pass

    def test_create_device(self):
        # Load the device file
        pass

    def test_record(self):
        pass

    def test_play(self):
        #self.evemu.play(self.get_events_file(), self.get_device_file())
        pass


if __name__ == "__main__":
    unittest.main()
