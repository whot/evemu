import ctypes
import os

from evemu import base
from evemu import const
from evemu import exception
from evemu import util


class EvEmuDevice(base.EvEmuBase):
    """
    A wrapper class for the evemu device fucntions.
    """
    def __init__(self, library):
        super(EvEmuDevice, self).__init__(library)
        # the path to the node that will be the virtual device
        self._node = ""
        # the stream produced by fopen (used to open the virtual device
        # description file)
        self._device_file_stream = None
        # the file descriptor used by ioctl to create the virtual device
        self._uinput_fd = None
        try:
            self._new()
        except exception.EvEmuError:
            self.delete()
            # XXX re-raise the exception with a message

    def __del__(self):
        self.delete()
        self._device_file_stream = None
        self.close()
        self.destroy()
        if self.get_node_name() and os.path.exists(self.get_node_name()):
            os.unlink(self.get_node_name())

    def _new(self):
        device_new = self.get_lib().evemu_new
        device_new.restype = ctypes.c_void_p
        # The C API expects a device name to be passed, however, it doesn't do
        # anything with it, so we're not going to provide it as an option in
        # the Python API.
        self._device_pointer = device_new("")

    @property
    def _as_parameter_(self):
        return self.get_deivce_pointer()

    def get_lib(self):
        return self._lib

    def get_device_pointer(self):
        return self._device_pointer

    def get_node_name(self):
        if not self._node:
            self._node = util.get_next_device()
        return self._node

    def delete(self):
        """
        Frees up the memory associated with the pointer (and deletes the
        pointer).

        This is done when:
         * uncessessfully attempting to create a new device data structure
         * unsuccessfully attempting to read the device description file
         * unsuccessfully attempting to open the UINPUT_NODE for writing

        Note that when uncsuccessfully calling evemu_create, just the close
        operation is performed, nothing else.
        """
        self._call(self.get_lib().evemu_delete, self.get_device_pointer())

    def destroy(self):
        """
        Deletes the /dev/device/eventXX device that was created.

        This is done when:
         * successfully setup up the eventXX device, after all the work is done

        Note that when uncsuccessfully calling evemu_create, just the close
        operation is performed, nothing else.
        """
        self._call(self.get_lib().evemu_delete, self._uinput_fd)

    def close(self):
        """
        Closes any open fds.

        This is done when:
         * unsuccessfully calling evemu_create
        """
        if self._uinput_fd:
            os.close(self._uinput_fd)

    def read(self, device_file):
        # pre-load the device structure with data from the virtual device
        # description file
        try:
            self._device_file_stream = self._call(
                self.get_c_lib().fopen, device_file, "r")
        except exception.EvEmuError:
            self.delete()
            # XXX re-raise the exception with a message
        self._call(
            self.get_lib().evemu_read,
            self.get_device_pointer(),
            self._device_file_stream)

    def create_node(self, device_file):
        # load device data from the virtual device description file into the
        # data structure referenced by the device pointer
        self.read(device_file)
        # create the node
        try:
            self._uinput_fd = os.open(const.UINPUT_NODE, os.O_WRONLY)
        except exception.EvEmuError:
            self.delete()
            # XXX re-raise the exception with a message
        # populate the new node with data from the device pointer
        try:
            self._call(
                self.get_lib().evemu_create,
                self.get_device_pointer(),
                self._uinput_fd)
        except exception.EvEmuError, e:
            self.close()
            # XXX re-raise the exception with a message

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
