import ctypes
import os
import tempfile

from evemu import base
from evemu.exception import WrapperError, ExecutionError


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
