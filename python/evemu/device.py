import ctypes
import os

from evemu import base
from evemu import const
from evemu import util


class EvEmuDevice(base.EvEmuBase):
    """
    A wrapper class for the evemu device fucntions.
    """
    def __init__(self, device_name, library):
        super(EvEmuDevice, self).__init__(library)
        device_new = self._lib.evemu_new
        device_new.restype = ctypes.c_void_p
        self._device = device_new(device_name)
        self._node = ""

    def __del__(self):
        if self.get_node_name() and os.path.exists(self.get_node_name()):
            os.unlink(self.get_node_name())
        self.get_lib().evemu_delete(self._device)

    @property
    def _as_property_(self):
        return self.get_deivce_fd()

    def get_lib(self):
        return self._lib

    def get_device_fd(self):
        return self._device

    def get_node_name(self):
        if not self._node:
            self._node = util.get_next_device()
        return self._node

    def read(self, device_file):
        # pre-load the device structure with data from the 
        stream = self._call(self.get_c_lib().fopen, device_file)
        #import pdb;pdb.set_trace()
        self._call(
            self.get_lib().evemu_read, self.get_device_fd(),
            ctypes.byref(ctypes.c_int(stream)))

    def create_node(self, device_file):
        # load device data from the device_file
        self.read(device_file)
        # create the node
        input_fd = os.open(const.UINPUT_NODE, os.O_WRONLY)
        self._call(self.get_lib().evemu_create, self.get_device_fd(), input_fd)
        # write the device file to the new node
        #source_file = open(device_file)
        #dest_file = open(self.get_node_name(), "w")
        #dest_file.write(source_file.read())
        #source_file.close()
        #dest_file.close()
        #os.close(input_fd)

    @property
    def version(self):
        return self.get_lib().evemu_get_version(self.get_device_fd())

    @property
    def name(self):
        return self.get_lib().evemu_get_name(self.get_device_fd())

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
