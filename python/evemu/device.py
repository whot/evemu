import ctypes
import os

from evemu import base
from evemu import const
from evemu import exception
from evemu import util


class EvEmuDevice(base.EvEmuBase):
    """
    A wrapper class for the evemu device fucntions.

    For the methods with the @property decorator, as well as the the get_* and
    has_* methods, the following notes apply:

    The medhod parameters 'event_type' and 'event_code' take their meanings
    from the input event system in linux (the input_event struct defined in
    linux/input.h).

    Ordinarily, to know a code, one must first know the type. However, in our
    case, we mostly just case about multi-touch. Since MT data only uses
    EV_ABS, it is understood that methods without a type are implicitly
    expecting a context of EV_ABS.

    As such, for those methods, the valid codes are the ABS_* values listed in
    the evemu.const module.

    @event_type:  one of the EV_* constants

    @event_code: a code related to the event type
    """
    def __init__(self, library):
        super(EvEmuDevice, self).__init__(library)
        # the path to the node that will be the virtual device
        self._node = ""
        # the stream produced by fopen (used to open the virtual device
        # description file)
        self._device_file_stream = None
        # the python variable that holds the reference to the C pointer for the
        # device data structure; ctypes handles the byref internals via the
        # _as_parameter_ method magic
        self._device_pointer = None
        # the file descriptor used by ioctl to create the virtual device
        self._uinput_fd = None
        try:
            self._new()
        except exception.EvEmuError, error:
            self.delete()
            raise error

    def __del__(self):
        self.delete()
        self._device_file_stream = None
        self.destroy()
        self.close()
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
        if self.get_device_pointer():
            self._call(self.get_lib().evemu_delete, self.get_device_pointer())
        self._device_pointer = None

    def destroy(self):
        """
        Deletes the /dev/device/eventXX device that was created.

        This is done when:
         * successfully setup up the eventXX device, after all the work is done

        Note that when uncsuccessfully calling evemu_create, just the close
        operation is performed, nothing else.
        """
        if self._uinput_fd:
            self._call(self.get_lib().evemu_destroy, self._uinput_fd)

    def close(self):
        """
        Closes the uinput device.

        This is done when:
         * unsuccessfully calling evemu_create
        """
        if self._uinput_fd:
            os.close(self._uinput_fd)
        self._uinput_fd = None

    def _read(self, device_file):
        self._device_file_stream = self._call(
            self.get_c_lib().fopen, device_file, "r")
        self._call(
            self.get_lib().evemu_read,
            self.get_device_pointer(),
            self._device_file_stream)

    def read(self, device_file):
        """
        Pre-load the device structure with data from the virtual device
        description file.
        """
        try:
            self._read(device_file)
        except exception.EvEmuError, error:
            self.delete()
            raise error

    def _open_uinput(self):
            self._uinput_fd = os.open(const.UINPUT_NODE, os.O_WRONLY)

    def _create(self):
        self._call(
            self.get_lib().evemu_create,
            self.get_device_pointer(),
            self._uinput_fd)

    def create_node(self, device_file):
        # load device data from the virtual device description file into the
        # data structure referenced by the device pointer
        self.read(device_file)
        # create the node
        try:
            self._open_uinput()
        except exception.EvEmuError, error:
            self.delete()
            raise error
        # populate the new node with data from the device pointer
        try:
            self._create()
        except exception.EvEmuError, error:
            self.close()
            raise error

    def write(self, filename):
        """
        Whatever data has been stored in the struct will get written to the
        passed file.
        """
        import sys
        output_fd = os.open(filename, os.O_WRONLY)
        import pdb;pdb.set_trace()
        self._call(
            self.get_lib().evemu_write, 
            self.get_device_pointer(),
            sys.stdout.fileno())
            #output_fd)
        os.close(output_fd)

    def extract(self, device_node):
        """
        A linux input device node is opened and read, storing all the retrieved
        data in the device data structure.
        """

    # Property methods
    @property
    def version(self):
        return self._call(
            self.get_lib().evemu_get_version, 
            self.get_device_pointer())

    @property
    def name(self):
        func = self.get_lib().evemu_get_name
        func.restype = ctypes.c_char_p
        return self._call(func, self.get_device_pointer())

    @property
    def id_bustype(self):
        return self._call(
            self.get_lib().evemu_get_id_bustype, 
            self.get_device_pointer())

    @property
    def id_vendor(self):
        return self._call(
            self.get_lib().evemu_get_id_vendor, 
            self.get_device_pointer())

    @property
    def id_product(self):
        return self._call(
            self.get_lib().evemu_get_id_product, 
            self.get_device_pointer())

    @property
    def id_version(self):
        return self._call(
            self.get_lib().evemu_get_id_version, 
            self.get_device_pointer())

    # Getter methods
    def get_abs_minimum(self, event_code):
        return self._call(
            self.get_lib().evemu_get_abs_minimum, 
            self.get_device_pointer(),
            int(event_code))

    def get_abs_maximum(self, event_code):
        return self._call(
            self.get_lib().evemu_get_abs_maximum, 
            self.get_device_pointer(),
            event_code)

    def get_abs_fuzz(self, event_code):
        return self._call(
            self.get_lib().evemu_get_abs_fuzz, 
            self.get_device_pointer(),
            event_code)

    def get_abs_flat(self, event_code):
        return self._call(
            self.get_lib().evemu_get_abs_flat, 
            self.get_device_pointer(),
            event_code)

    def get_abs_resolution(self, event_code):
        return self._call(
            self.get_lib().evemu_get_abs_resolution, 
            self.get_device_pointer(),
            event_code)

    def has_prop(self, event_code):
        return self._call(
            self.get_lib().evemu_has_prop, 
            self.get_device_pointer(),
            event_code)

    def has_event(self, event_type, event_code):
        """
        This method's 'even_type' parameter is expected to mostly take the
        value for EV_ABS (i.e., 0x03), but may on occasion EV_KEY (i.e., 0x01).
        If the former, then the even_code parameter will take the same values
        as the methods above (ABS_*). However, if the latter, then the legal
        values will be BTN_*.

        The reason for including the button data, is that buttons are sometimes
        used to simulate gestures for a higher number of touches than are
        possible with just 2-touch hardware.
        """
        return self._call(
            self.get_lib().evemu_has_event, 
            self.get_device_pointer(),
            event_type,
            event_code)
