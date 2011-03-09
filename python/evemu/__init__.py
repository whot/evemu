from ctypes import CDLL
from ctypes.util import find_library


LIB = "libutouch-evemu"


class Device(object):
    """
    """
    def __init__(self, description_file):
        pass


class EvEmu(object):
    """
    """
    def __init__(self, library=""):
        """
        """
        if not library:
            library = find_library(LIB)
        self._evemu = CDLL(library)

    def describe(self):
        """
        The describe gathers information about the input device and prints it
        to stdout. This information can be parsed by the create_device to
        create a virtual input device with the same properties.

        Scripts that use this method need to be run as root.
        """

    def create_device(self, description_file):
        """
        The create_device method creates a virtual input device based on the
        provided description-file. This description is usually created by the
        describe method. create_device then creates a new input device with
        uinput and prints the name and the device file to stdout.

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
        the form created by evemu-record(1).

        Scripts that use this method need to be run as root.
        """



