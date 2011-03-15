import ctypes
import os

from evemu import base
from evemu import const
from evemu import util


class EvEmuDevice(base.EvEmuBase):
    """
    A wrapper class for the evemu device fucntions.
    """
    def __init__(self, library):
        super(EvEmuDevice, self).__init__(library)
        device_new = self._lib.evemu_new
        device_new.restype = ctypes.c_void_p
        # The C API expects a device name to be passed, however, it doesn't do
        # anything with it, so we're not going to provide it as an option in
        # the Python API.
        self._device_pointer = device_new("")
        self._node = ""
        self._device_file_stream = None
        self._uinput_fd = None

    def __del__(self):
        self.get_lib().evemu_delete(self._device_pointer)
        del(self._device_file_stream)
        if self._uinput_fd:
            os.close(self._uinput_fd)
        if self.get_node_name() and os.path.exists(self.get_node_name()):
            os.unlink(self.get_node_name())

    @property
    def _as_property_(self):
        return self.get_deivce_fd()

    def get_lib(self):
        return self._lib

    def get_device_pointer(self):
        return self._device_pointer

    def get_node_name(self):
        if not self._node:
            self._node = util.get_next_device()
        return self._node

    def read(self, device_file):
        # pre-load the device structure with data from the 
        self._device_file_stream = self._call(
            self.get_c_lib().fopen, device_file, "r")
        self._call(
            self.get_lib().evemu_read,
            self.get_device_pointer(),
            self._device_file_stream)

    def create_node(self, device_file):
        # load device data from the device_file
        self.read(device_file)
        # create the node
        self._input_fd = os.open(const.UINPUT_NODE, os.O_WRONLY)
        self._call(
            self.get_lib().evemu_create, self.get_device_pointer(), self._input_fd)

    @property
    def version(self):
        return self.get_lib().evemu_get_version(self.get_device_pointer())

    @property
    def name(self):
        return self.get_lib().evemu_get_name(self.get_device_pointer())

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

    def has_prop(self, code):
        pass

    def has_event(self, event_type, code):
        pass
