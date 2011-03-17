import unittest

from evemu.script import EvEmu
from evemu.testing import testcase


class EvEmuTestCase(testcase.BaseTestCase):

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
