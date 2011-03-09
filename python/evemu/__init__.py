from ctypes import CDLL
from ctypes.util import find_library
import sys


LIB = "libutouch-evemu"


class EvEmu(object):
    """
    """
    def __init__(self, library=""):
        """
        """
        if not library:
            library = find_library(LIB)
        self._evemu = CDLL(library)
        self._virtual_device = None

    def describe(self, path_to_touch_device):
        """
        The describe gathers information about the input device and prints it
        to stdout. This information can be parsed by the create_device to
        create a virtual input device with the same properties.

        Scripts that use this method need to be run as root.
        """
        fd = open(path_to_touch_device, "r")
        device = self._evemu.evemu_new(0)
        # XXX check for device being not none, err out if so
        data = self._evemu.evemu_extract(device, fd)
        # XXX check for data being not none, err out if so
        fd.close()
        # XXX I don't like writing to stdout by default with a library. I'd
        # prever this be an option. For now, we'll duplicate the scripts and
        # keep it as is...
        self._evemu.evemu_write(device, sys.stdout)
        return data

    def create_device(self, description_file):
        """
        The create_device method creates a virtual input device based on the
        provided description-file. This description will have been created by
        the describe method. The create_device method then creates a new input
        device with uinput and prints the name and the device file to stdout.

        Scripts that use this method need to be run as root.
        """

    def record(self):
        """
        This method captures events from the input device and prints them to
        stdout. The events can be parsed by the play method, allowing a virtual
        input device created with the create_device method to emit the exact
        same event sequence.

        Scripts that use this method need to be run as root.
        """

    def play(self, events_file):
        """
        The play method replays the event sequence, as provided by the
        events-file, through the input device. The event sequence must be in
        the form created by the record method.

        Scripts that use this method need to be run as root.
        """



