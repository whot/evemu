import unittest

import evemu.base
import evemu.const
import evemu.testing.testcase


class EvEmuBaseTestCase(evemu.testing.testcase.BaseTestCase):

    def test_so_library_found(self):
        wrapper = evemu.base.EvEmuBase()
        # Make sure that the library loads
        self.assertNotEqual(
            wrapper._lib._name.find("libevemu"), -1)

    def test_c_symbols_found(self):
        # Make sure that the expected functions are present
        wrapper = evemu.base.EvEmuBase()
        for function_name in evemu.const.API:
            function = getattr(wrapper._lib, function_name)
            self.assertTrue(function is not None)


if __name__ == "__main__":
    unittest.main()
