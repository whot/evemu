import ctypes

from evemu import base


class _EvEmuDevice(ctypes.Structure):
    pass


class EvEmuDevice(base.EvEmuBase):
    """
    A wrapper class for the evemu device fucntions.
    """
    def __init__(self, library, device):
        super(EvEmuDevice, self).__init__(library)
        self._device = device

    @property
    def version(self):
        pass

    @property
    def name(self):
        pass

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
