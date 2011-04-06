import ctypes
import os
import tempfile

from evemu import base
from evemu import const
from evemu import device
from evemu.exception import ExecutionError


class EvEmuWrapper(base.EvEmuBase):
    """
    This class wraps the functionality offered by several of the evemu command
    line tools.
    """
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

    def describe(self, device_path, output_file):
        """
        """
        self.device.extract(device_path)
        self.device.write(output_file)

    def play(self):
        pass

    def record(self):
        pass
