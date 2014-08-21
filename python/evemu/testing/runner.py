import os
import unittest

import evemu.testing.result
import evemu.tests


def get_test_directory():
    return evemu.tests.__path__[0]


class CustomTestRunner(unittest.TextTestRunner):
    """
    This is only needed for Python 2.6 and lower.
    """
    def _makeResult(self):
        return evemu.testing.result.CustomTestResult(
            self.stream, self.descriptions, self.verbosity)


def get_suite(loader, top_level_directory):
    if hasattr(loader, "discover"):
        # Python 2.7
        suite = loader.discover(top_level_directory)
    else:
        # Python 2.4, 2.5, 2.6
        names = []
        def _path_to_module(path):
            # generate dotted names for file paths
            path = path.replace(".py", "")
            return path.replace("/", ".")

        # walk the directory
        for dirpath, dirnames, filenames in os.walk(top_level_directory):
            modules = [
                _path_to_module(os.path.join(dirpath, x)) for x in filenames
                    if x.startswith("test_") and x.endswith(".py")]
            if not modules:
                continue
            names.extend(modules)
        suite = loader.loadTestsFromNames(names)
    return suite


def get_runner():
    try:
        # Python 2.7
        runner = unittest.TextTestRunner(
            verbosity=2, resultclass=evemu.testing.result.CustomTestResult)
    except TypeError:
        # Python 2.4, 2.5, 2.6
        runner = CustomTestRunner(verbosity=2)
    return runner


def run_tests():
    loader = unittest.TestLoader()
    suite = get_suite(loader, get_test_directory())
    return get_runner().run(suite)


if __name__ == "__main__":
    import sys
    result = run_tests()
    if not result.wasSuccessful():
        sys.exit(1)
