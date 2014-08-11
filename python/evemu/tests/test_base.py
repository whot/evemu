import unittest

import evemu.base
import evemu.testing.testcase


class EvEmuBaseTestCase(evemu.testing.testcase.BaseTestCase):

    def test_libc_found(self):
        lib = evemu.base.LibC._load()
        self.assertNotEqual(lib, None)
        self.assertTrue(lib._name.startswith("libc"))

    def test_libc_static_from_load(self):
        first = evemu.base.LibC._load()
        self.assertNotEqual(first, None)

        second = evemu.base.LibC._load()
        self.assertNotEqual(second, None)

        self.assertEqual(first, second)

    def test_libc_static_in_object(self):
        first = evemu.base.LibC()
        self.assertNotEqual(first, None)

        second = evemu.base.LibC()
        self.assertNotEqual(second, None)

        self.assertEqual(first._loaded_lib, second._loaded_lib)

    def test_libevemu_found(self):
        lib = evemu.base.LibEvemu._load()
        self.assertNotEqual(lib, None)
        self.assertTrue(lib._name.startswith("libevemu"))

    def test_libevemu_static_from_load(self):
        first = evemu.base.LibEvemu._load()
        self.assertNotEqual(first, None)

        second = evemu.base.LibEvemu._load()
        self.assertNotEqual(second, None)

        self.assertEqual(first, second)

    def test_libevemu_static_in_object(self):
        first = evemu.base.LibEvemu()
        self.assertNotEqual(first, None)

        second = evemu.base.LibEvemu()
        self.assertNotEqual(second, None)

        self.assertEqual(first._loaded_lib, second._loaded_lib)

if __name__ == "__main__":
    unittest.main()
