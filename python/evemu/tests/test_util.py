import unittest

from evemu import util

class UtilTestCase(unittest.TestCase):

    def test_lsinput(self):
        results = util.lsinput()
        self.assertIn("/dev/input/event", results)
        self.assertIn("bustype", results)
        self.assertIn("name", results)
        self.assertIn("product", results)
        self.assertIn("version", results)

    def test_get_test_directory(self):
        result = util.get_test_directory()
        self.assertEqual(result, "evemu/tests")

    def test_get_test_module(self):
        result = util.get_test_module()
        self.assertEqual(result, "evemu.tests")


if __name__ == "__main__":
    unittest.main()
