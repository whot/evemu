from ctypes.util import find_library
import os
import tempfile
import unittest

from evemu import base, const, device, exception, script, wrapper
from evemu.testing.base import BaseTestCase


class EvEmuBaseTestCase(BaseTestCase):

    def test_initialize(self):
        wrapper = base.EvEmuBase(self.library)
        # Make sure that the library loads
        self.assertNotEqual(
            wrapper._lib._name.find("libutouch-evemu"), -1)
        # Make sure that the expected functions are present
        for function_name in const.API:
            function = getattr(wrapper._lib, function_name)
            self.assertTrue(function is not None)


if __name__ == "__main__":
    unittest.main()
