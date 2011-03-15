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
        all fields to zero. If name is non-null and the length is sane, it is
        copied to the device name.
        """
        super(EvEmuWrapper, self).__init__(library)
        self.device = device.EvEmuDevice(library)

    def _as_parameter_(self):
        return self.get_device()

    def get_device(self):
        return self.device.get_device_fd()

    def read(self, filename):
        # XXX this may be borked and thus may need to be re-examined
        stream = self._call(self.get_c_lib().fopen, filename)
        return self._call(self.get_lib().evemu_read, self.get_device(), stream)

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
        # XXX now destroy the device?
        #self._call(self.get_lib().evemu_destroy, input_fd)
        #return (virtual_input_device, virtual_input_fd)

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
