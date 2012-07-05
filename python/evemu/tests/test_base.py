import unittest

from evemu import const
from evemu.base import EvEmuBase
from evemu.testing import testcase


class EvEmuBaseTestCase(testcase.BaseTestCase):

    def test_so_library_found(self):
        wrapper = EvEmuBase(self.library)
        # Make sure that the library loads
        self.assertNotEqual(
            wrapper._lib._name.find("libevemu"), -1)

    def test_c_symbols_found(self):
        # Make sure that the expected functions are present
        wrapper = EvEmuBase(self.library)
        for function_name in const.API:
            function = getattr(wrapper._lib, function_name)
            self.assertTrue(function is not None)


if __name__ == "__main__":
    unittest.main()
