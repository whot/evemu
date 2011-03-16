LIB = "libutouch-evemu"
DEFAULT_LIB = "/usr/lib/libutouch-evemu.so"
LOCAL_LIB = "../src/.libs/libutouch-evemu.so"
UINPUT_NODE = "/dev/uinput"
MAX_EVENT_NODE = 32
DEVICE_PATH_TEMPLATE = "/dev/input/event%d"
DEVICE_NAME_PATH_TEMPLATE = "/sys/class/input/event%d/device/name"
# The following should be examined every release of evemu
API = [
    "evemu_new",
    "evemu_delete",
    "evemu_extract",
    "evemu_write",
    "evemu_read",
    "evemu_write_event",
    "evemu_record",
    "evemu_read_event",
    "evemu_play",
    "evemu_create",
    "evemu_destroy",
    # Device functions
    "evemu_get_version",
    "evemu_get_name",
    "evemu_get_id_bustype",
    "evemu_get_id_vendor",
    "evemu_get_id_product",
    "evemu_get_id_version",
    "evemu_get_abs_minimum",
    "evemu_get_abs_maximum",
    "evemu_get_abs_fuzz",
    "evemu_get_abs_flat",
    "evemu_get_abs_resolution",
    "evemu_has_prop",
    "evemu_has_event",
    ]

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04
EV_SW = 0x05
EV_LED = 0x11
EV_SND = 0x12
EV_REP = 0x14
EV_FF = 0x15
EV_PWR = 0x16
EV_FF_STATUS = 0x17
EV_MAX = 0x1f
EV_CNT = EV_MAX + 1

EV_NAMES = {
    EV_SYN: "Sync",
    EV_KEY: "Keys or Buttons",
    EV_REL: "Relative Axes",
    EV_ABS: "Absolute Axes",
    EV_MSC: "Miscellaneous",
    EV_SW: "Switches",
    EV_LED: "Leds",
    EV_SND: "Sound",
    EV_REP: "Repeat",
    EV_FF: "Force Feedback",
    EV_PWR: "Power Management",
    EV_FF_STATUS: "Force Feedback Status",
}

# Relative axes
REL_X = 0x00
REL_Y = 0x01
REL_Z = 0x02
REL_RX = 0x03
REL_RY = 0x04
REL_RZ = 0x05
REL_HWHEEL = 0x06
REL_DIAL = 0x07
REL_WHEEL = 0x08
REL_MISC = 0x09
REL_MAX = 0x0f
REL_CNT = REL_MAX+1

# Absolute axes
ABS_X = 0x00
ABS_Y = 0x01
ABS_Z = 0x02
ABS_RX = 0x03
ABS_RY = 0x04
ABS_RZ = 0x05
ABS_THROTTLE = 0x06
ABS_RUDDER = 0x07
ABS_WHEEL = 0x08
ABS_GAS = 0x09
ABS_BRAKE = 0x0a
ABS_HAT0X = 0x10
ABS_HAT0Y = 0x11
ABS_HAT1X = 0x12
ABS_HAT1Y = 0x13
ABS_HAT2X = 0x14
ABS_HAT2Y = 0x15
ABS_HAT3X = 0x16
ABS_HAT3Y = 0x17
ABS_PRESSURE = 0x18
ABS_DISTANCE = 0x19
ABS_TILT_X = 0x1a
ABS_TILT_Y = 0x1b
ABS_TOOL_WIDTH = 0x1c
ABS_VOLUME = 0x20
ABS_MISC = 0x28
ABS_MT_SLOT = 0x2f  # MT slot being modified
ABS_MT_TOUCH_MAJOR = 0x30  # Major axis of touching ellipse
ABS_MT_TOUCH_MINOR = 0x31  # Minor axis (omit if circular)
ABS_MT_WIDTH_MAJOR = 0x32  # Major axis of approaching ellipse
ABS_MT_WIDTH_MINOR = 0x33  # Minor axis (omit if circular)
ABS_MT_ORIENTATION = 0x34  # Ellipse orientation
ABS_MT_POSITION_X = 0x35  # Center X ellipse position
ABS_MT_POSITION_Y = 0x36  # Center Y ellipse position
ABS_MT_TOOL_TYPE = 0x37  # Type of touching device
ABS_MT_BLOB_ID = 0x38  # Group a set of packets as a blob
ABS_MT_TRACKING_ID = 0x39  # Unique ID of initiated contact
ABS_MT_PRESSURE = 0x3a  # Pressure on contact area
ABS_MAX = 0x3f
ABS_CNT = ABS_MAX+1
