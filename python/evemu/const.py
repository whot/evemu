LIB = "libutouch-evemu"
DEFAULT_LIB = "/usr/lib/libutouch-evemu.so"
LOCAL_LIB = "../src/.libs/libutouch-evemu.so"
UINPUT_NODE = "/dev/uinput"
MAX_EVENT_NODE = 32
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
