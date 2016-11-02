"""
The base module provides classes wrapping shared libraries.
"""
import ctypes
import ctypes.util
import os

# Import types directly, so they don't have to be prefixed with "ctypes.".
from ctypes import c_char_p, c_int, c_uint, c_void_p, c_long, c_int32, c_uint16

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
                strargs.append('"%s"' % args[num].decode("iso8859-1"))
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


class LibC(LibraryWrapper):
    """
    Wrapper for API calls to the C library.
    """

    @staticmethod
    def _cdll():
        return ctypes.CDLL("libc.so.6", use_errno=True)

    _api_prototypes = {
        "fdopen": {
            "argtypes": (c_int, c_char_p),
            "restype": c_void_p,
            "errcheck": expect_not_none
            },
        "fflush": {
            "argtypes": (c_void_p,),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        "rewind": {
            "argtypes": (c_void_p,),
            "restype": None,
            },
        }

class LibEvdev(LibraryWrapper):
    """
    Wrapper for API calls to libevdev
    """

    @staticmethod
    def _cdll():
        return ctypes.CDLL("libevdev.so", use_errno=True)

    _api_prototypes = {
        #const char *libevdev_event_type_get_name(unsigned int type);
        "libevdev_event_type_get_name": {
            "argtypes": (c_uint,),
            "restype": c_char_p
            },
        #int libevdev_event_type_from_name(const char *name);
        "libevdev_event_type_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
            },
        #const char *libevdev_event_code_get_name(unsigned int type, unsigned int code);
        "libevdev_event_code_get_name": {
            "argtypes": (c_uint, c_uint,),
            "restype": c_char_p
            },
        #int libevdev_event_code_from_name(unsigned int type, const char *name);
        "libevdev_event_code_from_name": {
            "argtypes": (c_uint, c_char_p,),
            "restype": c_int
            },
        #const char *libevdev_property_get_name(unsigned int prop);
        "libevdev_property_get_name": {
            "argtypes": (c_uint,),
            "restype": c_char_p
            },
        #int libevdev_property_from_name(const char *name);
        "libevdev_property_from_name": {
            "argtypes": (c_char_p,),
            "restype": c_int
            },
        }

class LibEvemu(LibraryWrapper):
    """
    Wrapper for API calls to the evemu library.
    """

    _LIBNAME = "libevemu.so"

    @staticmethod
    def _cdll():
        return ctypes.CDLL(LibEvemu._LIBNAME, use_errno=True)

    _api_prototypes = {
        #struct evemu_device *evemu_new(const char *name);
        "evemu_new": {
            "argtypes": (c_char_p,),
            "restype": c_void_p,
            "errcheck": expect_not_none
            },
        #void evemu_delete(struct evemu_device *dev);
        "evemu_delete": {
            "argtypes": (c_void_p,),
            "restype": None
            },
        #unsigned int evemu_get_version(const struct evemu_device *dev);
        "evemu_get_version": {
            "argtypes": (c_void_p,),
            "restype": c_uint,
            },
        #const char *evemu_get_name(const struct evemu_device *dev);
        "evemu_get_name": {
            "argtypes": (c_void_p,),
            "restype": c_char_p,
            "errcheck": expect_not_none
            },
        #void evemu_set_name(struct evemu_device *dev, const char *name);
        "evemu_set_name": {
            "argtypes": (c_void_p, c_char_p),
            "restype": None
            },
        #unsigned int evemu_get_id_bustype(const struct evemu_device *dev);
        "evemu_get_id_bustype": {
            "argtypes": (c_void_p,),
            "restype": c_uint
            },
        #void evemu_set_id_bustype(struct evemu_device *dev,
        #                          unsigned int bustype);
        "evemu_set_id_bustype": {
            "argtypes": (c_void_p, c_uint),
            "restype": None
            },
        #unsigned int evemu_get_id_vendor(const struct evemu_device *dev);
        "evemu_get_id_vendor": {
            "argtypes": (c_void_p,),
            "restype": c_uint
            },
        #void evemu_set_id_vendor(struct evemu_device *dev,
        #                         unsigned int vendor);
        "evemu_set_id_vendor": {
            "argtypes": (c_void_p, c_uint),
            "restype": None
            },
        #unsigned int evemu_get_id_product(const struct evemu_device *dev);
        "evemu_get_id_product": {
            "argtypes": (c_void_p,),
            "restype": c_uint
            },
        #void evemu_set_id_product(struct evemu_device *dev,
        #                          unsigned int product);
        "evemu_set_id_product": {
            "argtypes": (c_void_p, c_uint),
            "restype": None
            },
        #unsigned int evemu_get_id_version(const struct evemu_device *dev);
        "evemu_get_id_version": {
            "argtypes": (c_void_p,),
            "restype": c_uint
            },
        #void evemu_set_id_version(struct evemu_device *dev,
        #                          unsigned int version);
        "evemu_set_id_version": {
            "argtypes": (c_void_p, c_uint),
            "restype": None
            },
        #int evemu_get_abs_current_value(const struct evemu_device *dev,
        #                                int code);
        "evemu_get_abs_current_value": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #int evemu_get_abs_minimum(const struct evemu_device *dev, int code);
        "evemu_get_abs_minimum": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #void evemu_set_abs_minimum(struct evemu_device *dev, int code,
        #                           int min);
        "evemu_set_abs_minimum": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": None
            },
        #int evemu_get_abs_maximum(const struct evemu_device *dev, int code);
        "evemu_get_abs_maximum": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #void evemu_set_abs_maximum(struct evemu_device *dev, int code,
        #                           int max);
        "evemu_set_abs_maximum": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": None
            },
        #int evemu_get_abs_fuzz(const struct evemu_device *dev, int code);
        "evemu_get_abs_fuzz": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #void evemu_set_abs_fuzz(struct evemu_device *dev, int code, int fuzz);
        "evemu_set_abs_fuzz": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": None,
            },
        #int evemu_get_abs_flat(const struct evemu_device *dev, int code);
        "evemu_get_abs_flat": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #void evemu_set_abs_flat(struct evemu_device *dev, int code, int flat);
        "evemu_set_abs_flat": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": None
            },
        #int evemu_get_abs_resolution(const struct evemu_device *dev,
        #                             int code);
        "evemu_get_abs_resolution": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #void evemu_set_abs_resolution(struct evemu_device *dev, int code,
        #                              int res);
        "evemu_set_abs_resolution": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": None
            },
        #int evemu_has_prop(const struct evemu_device *dev, int code);
        "evemu_has_prop": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #int evemu_has_event(const struct evemu_device *dev, int type,
        #                    int code);
        "evemu_has_event": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #int evemu_has_bit(const struct evemu_device *dev, int type);
        "evemu_has_bit": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_ge_zero
            },
        #int evemu_extract(struct evemu_device *dev, int fd);
        "evemu_extract": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_write(const struct evemu_device *dev, FILE *fp);
        "evemu_write": {
            "argtypes": (c_void_p, c_void_p),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_read(struct evemu_device *dev, FILE *fp);
        "evemu_read": {
            "argtypes": (c_void_p, c_void_p),
            "restype": c_int,
            "errcheck": expect_gt_zero
            },
        #int evemu_write_event(FILE *fp, const struct input_event *ev);
        "evemu_write_event": {
            "argtypes": (c_void_p, c_void_p),
            "restype": c_int,
            "errcheck": expect_gt_zero
            },
        #int evemu_create_event(struct input_event *ev, int type, int code,
        #                       int value);
        "evemu_create_event": {
            "argtypes": (c_void_p, c_int, c_int, c_int),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_read_event(FILE *fp, struct input_event *ev);
        "evemu_read_event": {
            "argtypes": (c_void_p, c_void_p),
            "restype": c_int
            },
        #int evemu_read_event_realtime(FILE *fp, struct input_event *ev,
        #			      struct timeval *evtime);
        "evemu_read_event_realtime": {
            "argtypes": (c_void_p, c_void_p, c_void_p),
            "restype": c_int,
            "errcheck": expect_gt_zero
            },
        #int evemu_record(FILE *fp, int fd, int ms);
        "evemu_record": {
            "argtypes": (c_void_p, c_int, c_int),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_play_one(int fd, const struct input_event *ev);
        "evemu_play_one": {
            "argtypes": (c_int, c_void_p),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_play(FILE *fp, int fd);
        "evemu_play": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_create(struct evemu_device *dev, int fd);
        "evemu_create": {
            "argtypes": (c_void_p, c_int),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #int evemu_create_managed(struct evemu_device *dev);
        "evemu_create_managed": {
            "argtypes": (c_void_p,),
            "restype": c_int,
            "errcheck": expect_eq_zero
            },
        #void evemu_destroy(struct evemu_device *dev);
        "evemu_destroy": {
            "argtypes": (c_void_p,),
            "restype": None
            },
        }

class InputEvent(ctypes.Structure):
    _fields_ = [("sec", c_long),
		("usec", c_long),
		("type", c_uint16),
		("code", c_uint16),
		("value", c_int32)]
