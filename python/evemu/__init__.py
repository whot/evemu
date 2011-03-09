import cStringIO
import ctypes
from ctypes.util import find_library
import os
import sys
import tempfile


LIB = "libutouch-evemu"


# XXX move exceptions into their own module
class WrapperError(Exception):
    pass


# XXX Move base classes and other supporting classes into their own module(s)
class EvEmuBase(object):
    """
    A base wrapper class for the evemu functions, accessed via ctypes.
    """
    def __init__(self, library):
        self._evemu = ctypes.CDLL(library)
        self._libc = ctypes.CDLL(find_library("c"))


class EvEmuDevice(EvEmuBase):
    """
    A wrapper class for the evemu device fucntions.
    """
    def __init__(self, library, device):
        super(EvEmuDevice, self).__init__(library)
        self._device = device

    @property
    def version(self):
        pass

    @property
    def name(self):
        pass

    @property
    def id_bustype(self):
        pass

    @property
    def id_vendor(self):
        pass

    @property
    def id_product(self):
        pass

    @property
    def id_version(self):
        pass

    def abs_minimum(self, code):
        pass

    def abs_maximum(self, code):
        pass

    def abs_fuzz(self, code):
        pass

    def abs_flat(self, code):
        pass

    def abs_resolution(self, code):
        pass

    def abs_minimum(self, code):
        pass

    def has_prop(self, code):
        pass

    def has_event(self, event_type, code):
        pass


def checkdevice(function):
    """
    This is a decorator to be used for all methods that require the
    ._device_pointer attribute to be set (in other words, by methods whose
    evemu_* functions take a device pointer as a parameter).
    """
    def wrapped(self, *args, **kwds):
        if not self._device_pointer:
            raise WrapperError(
                "No device name has been previously specifed with new().")
    return wrapped


class EvEmuWrapper(EvEmuBase):
    """
    A wrapper class for the evemu actions.
    """
    def __init__(self, library):
        super(EvEmuWrapper, self).__init__(library)
        self._device_pointer = None
        self._device_fd, self._device_filename = tempfile.mkstemp()

    def new(self, device_name):
        """
        @name: wanted input device name (or NULL to leave empty)
        
        This method allocates a new evemu device structure and initializes
        all fields to zero. If name is non-null and the length is sane, it is
        copied to the device name.

        The device name will be used in the device data, similarly as is
        presented by the device data that is viewable when you do the
        following:
          $ cat /proc/bus/input/devices
        """
        device_pointer = self._evemu.evemu_new(device_name)
        self._device_pointer = ctypes.pointer(ctypes.c_int(device_pointer))
        return self._device_pointer

    @checkdevice
    def read(self, filename):
        # XXX this one's borked and needs to be re-examined
        stream = self._libc.fopen(filename)
            #ctypes.byref(ctypes.c_char_p(filename)), 
            #ctypes.byref(ctypes.c_char_p("r")))
        return self._evemu.evemu_new(
            ctypes.byref(self._device_pointer),
            stream)

    def create(self):
        pass

    @checkdevice
    def extract(self, filename):
        input_fd = os.open(filename, os.O_RDONLY)
        self._evemu.evemu_extract(
            ctypes.byref(self._device_pointer), input_fd)
        (output_fd, output_filename) = tempfile.mkstemp()
        self._evemu.evemu_write(
            ctypes.byref(self._device_pointer), output_fd)
        return output_fd.read()

    def delete(self):
        pass

    def destroy(self):
        pass

    def write_event(self):
        pass

    def read_event(self):
        pass

    def play(self):
        pass

    def record(self):
        pass


class EvEmu(object):
    """
    """
    def __init__(self, library=""):
        """
        """
        if not library:
            library = find_library(LIB)
        self._wrapper = EvEmuWrapper(library)
        self._virtual_device = None

    def describe(self, path_to_touch_device):
        """
        The describe gathers information about the input device and prints it
        to stdout. This information can be parsed by the create_device to
        create a virtual input device with the same properties.

        Scripts that use this method need to be run as root.
        """
        fd = open(path_to_touch_device, "r")
        device = self._wrapper.evemu_new(0)
        # XXX check for device being not none, err out if so
        data = self._wrapper.evemu_extract(device, fd)
        # XXX check for data being not none, err out if so
        fd.close()
        # XXX I don't like writing to stdout by default with a library. I'd
        # prefer that this were an option. For now, we'll duplicate the scripts
        # and keep it as is...
        self._wrapper.evemu_write(device, sys.stdout)
        return data

    def create_device(self, device_description_file):
        """
        The create_device method creates a virtual input device based on the
        provided description-file. This description will have been created by
        the describe method. The create_device method then creates a new input
        device with uinput and prints the name and the device file to stdout.

        Scripts that use this method need to be run as root.
        """
        if self._virtual_device:
            return self._virtual_device

    def record(self):
        """
        This method captures events from the input device and prints them to
        stdout. The events can be parsed by the play method, allowing a virtual
        input device created with the create_device method to emit the exact
        same event sequence.

        Scripts that use this method need to be run as root.
        """

    def play(self, device_description_file="", events_file=""):
        """
        The play method replays the event sequence, as provided by the
        events-file, through the input device. The event sequence must be in
        the form created by the record method.

        Scripts that use this method need to be run as root.
        """
        device_fd = os.open(device_description_file, os.O_WRONLY)
        events_fd = os.open(events_file, os.O_WRONLY)
        self._wrapper.play(device_fd, events_fd)


