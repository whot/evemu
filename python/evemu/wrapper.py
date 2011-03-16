import ctypes
import os
import tempfile

from evemu import base
from evemu import const
from evemu import device
from evemu.exception import ExecutionError


class EvEmuWrapper(base.EvEmuBase):

    def __init__(self, library=""):
        """
        This method allocates a new evemu device structure and initializes
        all fields to zero.
        """
        super(EvEmuWrapper, self).__init__(library)
        self.device = device.EvEmuDevice(library)

    def __del__(self):
        del(self.device)

    @property
    def _as_parameter_(self):
        return self.get_device()

    def get_device(self):
        return self.device.get_device_pointer()

    def read(self, device_file):
        """
        Load data from the virtual device description file into the device
        object.
        """
        self.device.read(device_file)

    def extract(self, filename):
        """
        This extracts device information from an input device.

        This method cannot be used against pre-recorded device files. To
        extract data from pre-recorded device files, first create a virtual
        device, and then execute extract against that virtual input device.
        """
        # XXX is this crackful?
        input_fd = os.open(filename, os.O_RDONLY)
        # XXX is there a better way of doing this, than creating another file
        # to output to? Seems wasteful :-(
        (output_fd, output_filename) = tempfile.mkstemp()
        self._call(self.get_lib().evemu_extract, self.get_device(), input_fd)
        return os.read(output_fd, 1024)

    def create(self, device_file):
        self.device.create_node(device_file)

    # XXX maybe this isn't needed at this level of abstraction...
    def delete(self):
        """
        Frees up the memory associated with the pointer (and deletes the
        pointer).
        
        See the docstring for EvEmuDevice.delete for more info.
        """
        self.device.delete()

    # XXX maybe this isn't needed at this level of abstraction...
    def destroy(self):
        """
        Deletes the /dev/device/eventXX device that was created.

        See the docstring for EvEmuDevice.destroy for more info.
        """
        self.device.destroy()

    def describe(self):
        pass

    def play(self):
        pass

    def record(self):
        pass
