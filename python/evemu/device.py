import ctypes

from evemu import base


class EvEmuDevice(object):
    """
    A wrapper class for the evemu device fucntions.
    """
    def __init__(self, device_name, loaded_library):
        self._lib = loaded_library
        device_new = self._lib.evemu_new
        device_new.restype = ctypes.c_void_p
        self._device = device_new(device_name)

    def __del__(self):
        self.get_lib().evemu_delete(self._device)

    @property
    def _as_property_(self):
        return self.get_deivce_fd()

    def get_lib(self):
        return self._lib

    def get_device_fd(self):
        return self._device

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
