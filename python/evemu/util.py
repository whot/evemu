import os
import re
import subprocess

from evemu import const


def lsinput():
    command_parts = ["lsinput"]
    try:
        # Python 2.7
        output = subprocess.check_output(command_parts)
    except AttributeError:
        # Python 2.4, 2.5, 2.6
        output = subprocess.Popen(
            command_parts, stdout=subprocess.PIPE).communicate()[0]
    return output


def get_top_directory():
    import evemu
    return evemu.__path__[0]


def get_test_directory():
    from evemu import tests
    return tests.__path__[0]


def get_test_module():
    return get_test_directory().replace("/", ".")


def get_all_device_numbers():
    numbers = []
    for index in xrange(const.MAX_EVENT_NODE):
        path = const.DEVICE_PATH_TEMPLATE % index
        if os.path.exists(path):
            continue
        numbers.append(index)
    return numbers


def get_all_device_names():
    names = []
    for device_number in get_all_device_numbers():
        file_handle = open(const.DEVICE_NAME_PATH_TEMPLATE % device_number)
        names.append({"name": file_handle.read(), "id": device_number})
        file_handle.close()
    return names


def get_last_device_number():
    """
    Get the last used device node number.
    """
    return get_all_device_numbers()[0]


def get_last_device():
    """
    Get the last used device node.
    """
    return const.DEVICE_PATH_TEMPLATE % get_last_device_number()


def get_next_device():
    """
    Get the next availne device node.
    """
    next_number = get_last_device_number() + 1
    if next_number > const.MAX_EVENT_NODE:
        raise EvEmuError("device count exceeded MAX_EVENT_NODE")
    return const.DEVICE_PATH_TEMPLATE % next_number
