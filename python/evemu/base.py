import ctypes
import ctypes.util
import os

import evemu.const
import evemu.exception


class EvEmuBase(object):
    """
    A base wrapper class for the evemu functions, accessed via ctypes.
    """
    def __init__(self):
        self._lib = ctypes.CDLL(evemu.const.LIB, use_errno=True)
        self._libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

    def _call0(self, api_call, *parameters):
        result = api_call(*parameters)
        if result == 0 and self.get_c_errno() != 0:
            raise evemu.exception.ExecutionError("%s: %s" % (
                api_call.__name__, self.get_c_error()))
        return result

    def _call(self, api_call, *parameters):
        result = api_call(*parameters)
        if result < 0 and self.get_c_errno() != 0:
            raise evemu.exception.ExecutionError("%s: %s" % (
                api_call.__name__, self.get_c_error()))
        return result

    def get_c_errno(self):
        return ctypes.get_errno()

    def get_c_error(self):
        return os.strerror(ctypes.get_errno())

    def get_c_lib(self):
        return self._libc

    def get_lib(self):
        return self._lib
