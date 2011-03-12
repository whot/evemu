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


def get_last_device():
    """
    Get the last used device node number.
    """
    output = lsinput()
    return [x for x in output.splitlines() if '/dev/input/event' in x][-1]


def get_next_device():
    """
    Get the next availne device node number.
    """
    last_device = get_last_device()
    last_node_number = int(re.sub("[^0-9]", "", last_device))
    return "/dev/input/event%i" % (last_node_number + 1)


def get_next_device2():
    """
    Get the next availne device node number.
    """
    path_template = "/dev/input/event%d"
    for index in xrange(const.MAX_EVENT_NODE):
        path = path_template % index
        if not os.path.exists(path):
            return path
