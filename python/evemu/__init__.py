"""
The evemu module provides the Python interface to the kernel-level input device
raw events.
"""

# Copyright 2011-2012 Canonical Ltd.
# Copyright 2014 Red Hat, Inc.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License version 3 
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ctypes
import glob
import os
import re
import stat
import tempfile

import evemu.base
import evemu.event_names

__all__ = ["Device",
           "InputEvent",
           "event_get_value",
           "event_get_name",
           "input_prop_get_value",
           "input_prop_get_name"]

def event_get_value(event_type, event_code = None):
    """
    Return the integer-value for the given event type and/or code string
    e.g. "EV_ABS" returns 0x03, ("EV_ABS", "ABS_Y") returns 0x01.
    Unknown event types or type/code combinations return None.

    If an event code is passed, the event type may be given as integer or
    string.
    """
    try:
        return evemu.event_names._event_get_value(event_type, event_code)
    except KeyError:
        return None

def event_get_name(event_type, event_code = None):
    """
    Return the string-value for the given event type and/or code value
    e.g. 0x03 returns "EV_ABS", ("EV_ABS", 0x01) returns "ABS_Y"
    Unknown event types or type/code combinations return None.

    If an event code is passed, the event type may be given as integer or
    string.
    """
    try:
        return evemu.event_names._event_get_name(event_type, event_code)
    except KeyError:
        return None

def input_prop_get_name(prop):
    """
    Return the name of the input property, or None if undefined.
    """
    try:
        return evemu.event_names._input_prop_get_name(prop)
    except KeyError:
        return None

def input_prop_get_value(prop):
    """
    Return the value of the input property, or None if undefined.
    """
    try:
        return evemu.event_names._input_prop_get_value(prop)
    except KeyError:
        return None

class InputEvent(object):
    __slots__ = 'sec', 'usec', 'type', 'code', 'value'

    def __init__(self, sec, usec, type, code, value):
        self.sec = sec
        self.usec = usec
        self.type = type
        self.code = code
        self.value = value

    def __str__(self):
        f = tempfile.TemporaryFile()
        libc = evemu.base.LibC()
        fp = libc.fdopen(f.fileno(), b"w+")

        event = evemu.base.InputEvent()
        event.sec = self.sec
        event.usec = self.usec
        event.type = self.type
        event.code = self.code
        event.value = self.value

        libevemu = evemu.base.LibEvemu()
        libevemu.evemu_write_event(fp, ctypes.byref(event))
        libc.fflush(fp)
        f.seek(0)
        return f.readline().rstrip()

class Device(object):
    """
    Encapsulates a raw kernel input event device, either an existing one as
    reported by the kernel or a pseudodevice as created through a .prop file.
    """

    def __init__(self, f, create=True):
        """
        Initialize an evemu Device.

        args:
        f -- a file object or filename string for either an existing input
        device node (/dev/input/eventNN) or an evemu prop file that can be used
        to create a pseudo-device node.
        create -- If f points to an evemu prop file, 'create' specifies if a
        uinput device should be created
        """

        if type(f) == str:
            self._file = open(f)
        elif hasattr(f, "read"):
            self._file = f
        else:
            raise TypeError("expected file or file name")

        self._is_propfile = self._check_is_propfile(self._file)
        self._libc = evemu.base.LibC()
        self._libevemu = evemu.base.LibEvemu()

        self._evemu_device = self._libevemu.evemu_new(b"")

        if self._is_propfile:
            fs = self._libc.fdopen(self._file.fileno(), b"r")
            self._libevemu.evemu_read(self._evemu_device, fs)
            if create:
                self._file = self._create_devnode()
        else:
            self._libevemu.evemu_extract(self._evemu_device,
                                         self._file.fileno())

    def __del__(self):
        if hasattr(self, "_is_propfile") and self._is_propfile:
            self._file.close()
            self._libevemu.evemu_destroy(self._evemu_device)

    def _create_devnode(self):
        self._libevemu.evemu_create_managed(self._evemu_device)
        return open(self._find_newest_devnode(self.name), 'r+b', buffering=0)

    def _find_newest_devnode(self, target_name):
        newest_node = (None, float(0))
        for sysname in glob.glob("/sys/class/input/event*/device/name"):
            with open(sysname) as f:
                name = f.read().rstrip()
                if name == target_name:
                    ev = re.search("(event\d+)", sysname)
                    if ev:
                       devname = os.path.join("/dev/input", ev.group(1))
                       ctime = os.stat(devname).st_ctime
                       if ctime > newest_node[1]:
                           newest_node = (devname, ctime)
        return newest_node[0]

    def _check_is_propfile(self, f):
        if stat.S_ISCHR(os.fstat(f.fileno()).st_mode):
            return False

        result = False
        for line in f.readlines():
            if line.startswith("N:"):
                result = True
                break
            elif line.startswith("# EVEMU"):
                result = True
                break
            elif line[0] != "#":
                raise TypeError("file must be a device special or prop file")

        f.seek(0)
        return result

    def describe(self, prop_file):
        """
        Gathers information about the input device and prints it
        to prop_file. This information can be parsed later when constructing
        a Device to create a virtual input device with the same properties.

        Scripts that use this method need to be run as root.
        """
        if not hasattr(prop_file, "read"):
            raise TypeError("expected file")

        fs = self._libc.fdopen(prop_file.fileno(), b"w")
        self._libevemu.evemu_write(self._evemu_device, fs)
        self._libc.fflush(fs)

    def events(self, events_file=None):
        """
        Reads the events from the given file and returns them as a list of
        dicts.
        """
        if events_file:
            if not hasattr(events_file, "read"):
                raise TypeError("expected file")
        else:
            events_file = self._file

        fs = self._libc.fdopen(events_file.fileno(), b"r")
        event = evemu.base.InputEvent()
        while self._libevemu.evemu_read_event(fs, ctypes.byref(event)) > 0:
            yield InputEvent(event.sec, event.usec, event.type, event.code, event.value)

    def play(self, events_file):
        """
        Replays an event sequence, as provided by the events_file,
        through the input device. The event sequence must be in
        the form created by the record method.

        Scripts that use this method need to be run as root.
        """
        if not hasattr(events_file, "read"):
            raise TypeError("expected file")

        fs = self._libc.fdopen(events_file.fileno(), b"r")
        self._libevemu.evemu_play(fs, self._file.fileno())

    def record(self, events_file, timeout=10000):
        """
        Captures events from the input device and prints them to the
        events_file. The events can be parsed by the play method,
        allowing a virtual input device to emit the exact same event
        sequence.

        Scripts that use this method need to be run as root.
        """
        if not hasattr(events_file, "read"):
            raise TypeError("expected file")

        fs = self._libc.fdopen(events_file.fileno(), b"w")
        self._libevemu.evemu_record(fs, self._file.fileno(), timeout)
        self._libc.fflush(fs)

    @property
    def version(self):
        """
        Gets the version of the evemu library used to create the Device.
        """
        return self._libevemu.evemu_get_version(self._evemu_device)

    @property
    def devnode(self):
        """
        Gets the name of the /dev node of the input device.
        """
        return self._file.name

    @property
    def name(self):
        """
        Gets the name of the input device (as reported by the device).
        """
        result = self._libevemu.evemu_get_name(self._evemu_device)
        return result.decode("iso8859-1")

    @property
    def id_bustype(self):
        """
        Identifies the kernel device bustype.
        """
        return self._libevemu.evemu_get_id_bustype(self._evemu_device)

    @property
    def id_vendor(self):
        """
        Identifies the kernel device vendor.
        """
        return self._libevemu.evemu_get_id_vendor(self._evemu_device)

    @property
    def id_product(self):
        """
        Identifies the kernel device product.
        """
        return self._libevemu.evemu_get_id_product(self._evemu_device)

    @property
    def id_version(self):
        """
        Identifies the kernel device version.
        """
        return self._libevemu.evemu_get_id_version(self._evemu_device)

    def get_abs_minimum(self, event_code):
        if type(event_code) == str:
            event_code = evemu.event_get_value("EV_ABS", event_code)
        return self._libevemu.evemu_get_abs_minimum(self._evemu_device,
                                                    event_code)

    def get_abs_maximum(self, event_code):
        if type(event_code) == str:
            event_code = evemu.event_get_value("EV_ABS", event_code)
        return self._libevemu.evemu_get_abs_maximum(self._evemu_device,
                                                    event_code)

    def get_abs_fuzz(self, event_code):
        if type(event_code) == str:
            event_code = evemu.event_get_value("EV_ABS", event_code)
        return self._libevemu.evemu_get_abs_fuzz(self._evemu_device,
                                                 event_code)

    def get_abs_flat(self, event_code):
        if type(event_code) == str:
            event_code = evemu.event_get_value("EV_ABS", event_code)
        return self._libevemu.evemu_get_abs_flat(self._evemu_device,
                                                 event_code)

    def get_abs_resolution(self, event_code):
        if type(event_code) == str:
            event_code = evemu.event_get_value("EV_ABS", event_code)
        return self._libevemu.evemu_get_abs_resolution(self._evemu_device,
                                                       event_code)

    # don't change 'event_code' to prop, it breaks API
    def has_prop(self, event_code):
        if type(event_code) == str:
            event_code = evemu.input_prop_get_value(event_code)
        result = self._libevemu.evemu_has_prop(self._evemu_device, event_code)
        return bool(result)

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
        if type(event_type) == str:
            event_type = evemu.event_get_value(event_type)
        if type(event_code) == str:
            event_code = evemu.event_get_value(event_type, event_code)
        result = self._libevemu.evemu_has_event(self._evemu_device,
                                                event_type,
                                                event_code)
        return bool(result)

