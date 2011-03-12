import os
import re
import subprocess

from evemu import const


def lsinput():
    command_parts = ["lsinput"]
    return subprocess.check_output(command_parts)

def get_test_directory():
    from evemu import tests
    return tests.__path__[0]


def get_test_module():
    return get_test_directory().replace("/", ".")


def get_last_device_number():
    for index in xrange(const.MAX_EVENT_NODE):
        path = const.DEVICE_PATH_TEMPLATE % index
        if not os.path.exists(path):
            return index-1


def get_last_device():
    """
    Get the last used device node number.
    """
    return const.DEVICE_PATH_TEMPLATE % get_last_device_number()


def get_next_device():
    """
    Get the next availne device node number.
    """
    return const.DEVICE_PATH_TEMPLATE % (get_last_device_number() + 1)

