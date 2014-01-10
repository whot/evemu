"""
The base module provides classes wrapping shared libraries.
"""
import ctypes
import ctypes.util
import os

# Import types directly, so they don't have to be prefixed with "ctypes.".
from ctypes import c_char_p, c_int, c_uint, c_void_p

import evemu.const
import evemu.exception


def raise_error_if(raise_error, result, func, args):
    """
    Raise an ExecutionError for an unexpected result (raise_error == True).

    The exception message includes the API call (name) plus arguments, the
    unexpected result and, if errno is not zero, text describing the
    error number.
    """
    def get_call_str():
        """ Returns a str 'function_name(argument_values...)'. """
        strargs = []
        for (num, arg) in enumerate(func.argtypes):
            # convert args to str for readable output
            if arg == c_char_p:
                strargs.append('"%s"' % args[num].decode(evemu.const.ENCODING))
            elif arg == c_void_p:
                strargs.append(hex(int(args[num])))
            else:
                strargs.append(str(args[num]))
        return "%s(%s)" % (func.__name__, ", ".join(strargs))

    def get_retval_str():
        """ Returns a str with the unexpected return value. """
        return ", Unexpected return value: %s" % result

    def get_errno_str():
        """ Returns a str describing the error number or an empty string. """
        errno = ctypes.get_errno()
        if errno != 0:
            return ", errno[%d]: %s" % (errno, os.strerror(errno))
        else:
            return ""

    if raise_error:
        msg = "%s%s%s" % (get_call_str(), get_retval_str(), get_errno_str())
        raise evemu.exception.ExecutionError(msg)
    else:
        # If the errcheck function returns the argument tuple it receives
        # unchanged, ctypes continues the normal processing it does on the
        # output parameters.
        return args


def expect_eq_zero(result, func, args):
    """ Expect 'result' being equal to zero. """
    return raise_error_if(result != 0, result, func, args)


def expect_ge_zero(result, func, args):
    """ Expect 'result' being greater or equal to zero. """
    return raise_error_if(result < 0, result, func, args)


def expect_gt_zero(result, func, args):
    """ Expect 'result' being greater then zero. """
    return raise_error_if(result <= 0, result, func, args)


def expect_not_none(result, func, args):
    """ Expect 'result' being not None. """
    return raise_error_if(result is None, result, func, args)


class LibraryWrapper(object):
    """
    Base class for wrapping a shared library.
    """
    _loaded_lib = None
        # Class variable containing the instance returned by CDLL(), which
        # represents the shared library.
        # Initialized once, shared between all instances of this class.

    def __init__(self):
        super(LibraryWrapper, self).__init__()
        self._load()

    # Prototypes for the API calls to wrap. Needs to be overwritten by sub
    # classes.
    _api_prototypes = {
        #"API_CALL_NAME": {
        #    "argtypes": sequence of ARGUMENT TYPES,
        #    "restype": RETURN TYPE,
        #    "errcheck": callback for return value checking, optional
        #    },
        }

    @classmethod
    def _load(cls):
        """
        Returns an instance of the wrapped shared library.

        If not already initialized: set argument and return types on API
        calls and optionally a callback function for return value checking.
        Add the API call as attribute to the class at the end.
        """
        if cls._loaded_lib is not None:
            # Already initialized, just return it.
            return cls._loaded_lib

        # Get an instance of the wrapped shared library.
        cls._loaded_lib = cls._cdll()

        # Iterate the API call prototypes.
        for (name, attrs) in cls._api_prototypes.items():
            # Get the API call.
            api_call = getattr(cls._loaded_lib, name)
            # Add argument and return types.
            api_call.argtypes = attrs["argtypes"]
            api_call.restype = attrs["restype"]
            # Optionally, add a callback for return value checking.
            if "errcheck" in attrs:
                api_call.errcheck = attrs["errcheck"]
            # Add the API call as attribute to the class.
            setattr(cls, name, api_call)

        return cls._loaded_lib

    @staticmethod
    # @abc.abstractmethod - Would be nice here, but it can't be mixed with
    #                       @staticmethod until Python 3.3.
    def _cdll():
        """ Returns a new instance of the wrapped shared library. """
        raise NotImplementedError


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
