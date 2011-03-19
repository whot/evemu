import ctypes

from evemu import const


ABS_CNT = const.ABS_MAX + 1


class InputIdStruct(ctypes.Structure):
    """
    Data structure based on input_id in linux/uinput.h.
    """
    _fields_ = [
        ("bustype", ctypes.c_uint),
        ("vendor", ctypes.c_uint),
        ("product", ctypes.c_uint),
        ("version", ctypes.c_uint),
        ]


class InputAbsInfoStruct(ctypes.Structure):
    """
    Data structure based on input_absinfo in XXX.
    """
    _fields_ = [
        ("value", ctypes.c_ulong),
        ("minimum", ctypes.c_ulong),
        ("maximum", ctypes.c_ulong),
        ("fuzz", ctypes.c_ulong),
        ("flat", ctypes.c_ulong),
        ("resolution", ctypes.c_ulong),
        ]


class EvEmuDeviceStruct(ctypes.Structure):
    """
    Data structure based on evemu_device in evemu-impl.h.
    """
    _fields_ = [
        ("version", ctypes.c_uint),
        ("name", ctypes.c_byte * const.UINPUT_MAX_NAME_SIZE),
        ("id", InputIdStruct),
        ("prop", ctypes.c_ubyte * const.EVPLAY_NBYTES),
        ("mask", ctypes.c_ubyte),
        ("pbytes", ctypes.c_int),
        ("mbytes", ctypes.c_int * const.EV_CNT),
        ("abs", InputAbsInfoStruct * ABS_CONT),
        ]
"""
struct evemu_device {
    unsigned int version;                       //
    char name[UINPUT_MAX_NAME_SIZE];            // string, max size
    struct input_id id;                         // struct input_id from linux/uinput.h
    unsigned char prop[EVPLAY_NBYTES];          //
    unsigned char mask[EV_CNT][EVPLAY_NBYTES];  // doubly indexed array...
    first index is what type, second field is a bitmask (
    int pbytes                                  //
    int mbytes[EV_CNT];                         // array of integers
    struct input_absinfo abs[ABS_CNT];          // array structures
};
"""
