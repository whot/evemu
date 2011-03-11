import cStringIO
import ctypes
import os
import sys
import tempfile

from evemu import base, const
from evemu.exception import WrapperError, ExecutionError


class EvEmuWrapper2(base.EvEmuBase):

    def __init__(self, device_name, library=""):
        super(EvEmuWrapper2, self).__init__(library)
        # XXX I feel like I'm not accounting for the fact that the device
        # pointer "points" to a struct... iow, should I be using
        # ctypes.Structure somwhere?
        device_new = self._lib.evemu_new
        device_new.restype = ctypes.c_void_p
        self._device = device_new(device_name)

    def __del__(self):
        self._lib.evemu_delete(self._device)

    def _as_parameter_(self):
        return self._device

    def read(self, filename):
        # XXX this may be borked and thus may need to be re-examined
        stream = self._libc.fopen(filename)
        if self.get_c_errno() != 0:
            raise ExecutionError, self.get_c_error()
        return self._lib.evemu_read(self._device, stream)

    def extract(self, filename):
        # XXX is this crackful?
        input_fd = os.open(filename, os.O_RDONLY)
        # XXX is there a better way of doing this, than creating another file
        # to output to? Seems wasteful :-(
        (output_fd, output_filename) = tempfile.mkstemp()
        ret_code = self._lib.evemu_extract(self._device, input_fd)
        if self.get_c_errno() != 0:
            raise ExecutionError, self.get_c_error()
        return self._lib.evemu_read(self._device, stream)
        import pdb;pdb.set_trace()
        print "return code: %s" % ret_code
        #self._lib.evemu_write(self._device, output_fd)
        return os.read(output_fd, 1024)


class EvEmuWrapper(base.EvEmuBase):
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
        device_pointer = self._lib.evemu_new(device_name)
        self._device_pointer = ctypes.pointer(ctypes.c_int(device_pointer))
        return self._device_pointer

    @property
    def _as_parameter(self):
        return ctypes.byref(self._device_pointer)

    def read(self, filename):
        # XXX this one's borked and needs to be re-examined
        stream = self._libc.fopen(filename)
            #ctypes.byref(ctypes.c_char_p(filename)), 
            #ctypes.byref(ctypes.c_char_p("r")))
        return self._lib.evemu_new(self._device_pointer, stream)

    def create(self):
        pass

    def extract(self, filename):
        input_fd = os.open(filename, os.O_RDONLY)
        self._lib.evemu_extract(self._device_pointer, input_fd)
        (output_fd, output_filename) = tempfile.mkstemp()
        self._lib.evemu_write(self._device_pointer, output_fd)
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
        pass

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


