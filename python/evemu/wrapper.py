import ctypes
import os
import tempfile

from evemu import base
from evemu import device
from evemu.exception import ExecutionError


class EvEmuWrapper(base.EvEmuBase):

    def __init__(self, device_name, library=""):
        """
        @device_name: wanted input device name (or NULL to leave empty)

        This method allocates a new evemu device structure and initializes
        all fields to zero. If name is non-null and the length is sane, it is
        copied to the device name.

        The device name will be used in the device data, similarly as is
        presented by the device data that is viewable when you do the
        following:
          $ cat /proc/bus/input/devices
        """
        super(EvEmuWrapper, self).__init__(library)
        self.device = device.EvEmuDevice(device_name, self.get_lib())

    def _as_parameter_(self):
        return self.get_device()

    def get_device(self):
        return self.device.get_raw_device()

    def read(self, filename):
        # XXX this may be borked and thus may need to be re-examined
        stream = self.get_c_lib().fopen(filename)
        if self.get_c_errno() != 0:
            raise ExecutionError, self.get_c_error()
        return self.get_lib().evemu_read(self.get_device(), stream)

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
        ret_code = self.get_lib().evemu_extract(self.get_device(), input_fd)
        if self.get_c_errno() != 0:
            raise ExecutionError, self.get_c_error()
        self._lib.evemu_write(self.get_device(), output_fd)
        return os.read(output_fd, 1024)

    def create(self):
        pass

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
