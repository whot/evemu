import unittest

from evemu import util
from evemu.testing import Non26BaseTestCase


class CommandsTestCase(Non26BaseTestCase):

    def test_lsinput_raw(self):
        results = util.lsinput_raw()
        self.assertIn("/dev/input/event", results)
        self.assertIn("bustype", results)
        self.assertIn("name", results)
        self.assertIn("product", results)
        self.assertIn("version", results)

    def test_lsinput(self):
        # let's just check the first one
        result = util.lsinput()[0]
        self.assertEqual(result.get("device"), "/dev/input/event0")
        self.assertTrue(result.get("bustype") is not None) 
        self.assertTrue(result.get("name") is not None) 
        self.assertTrue(result.get("product") is not None) 
        self.assertTrue(result.get("version") is not None) 


class DirectoriesTestCase(Non26BaseTestCase):

    def test_get_top_directory(self):
        result = util.get_top_directory()
        self.assertEqual(result, "evemu")

    def test_get_test_directory(self):
        result = util.get_test_directory()
        self.assertEqual(result, "evemu/tests")

    def test_get_test_module(self):
        result = util.get_test_module()
        self.assertEqual(result, "evemu.tests")


class DevicesTestCase(Non26BaseTestCase):

    def test_get_all_device_numbers(self):
        result = util.get_all_device_numbers()
        self.assertTrue(result != [])

    def test_get_all_device_names(self):
        result = util.get_all_device_names()
        self.assertTrue(result != [])

    def test_get_last_device_number(self):
        self.assertTrue(isinstance(util.get_last_device_number(), int))

    def test_get_last_device(self):
        result = util.get_last_device()
        self.assertIn("/dev/input/event", result)

    def test_get_next_device(self):
        last_device = util.get_last_device()
        next_device = util.get_next_device()
        self.assertIn("/dev/input/event", next_device)
        self.assertEqual(
            (int(last_device[-1]) + 1) % 10,
            int(next_device[-1]))


if __name__ == "__main__":
    unittest.main()
