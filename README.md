evemu - Kernel device emulation
===============================

The evemu library and tools are used to describe devices, record
data, create devices and replay data from kernel evdev devices.

http://wiki.freedesktop.org/wiki/Evemu
http://cgit.freedesktop.org/evemu/

Please file patches in the freedesktop.org bugzilla at
https://bugs.freedesktop.org/enter_bug.cgi?product=evemu

evemu produces two different data formats, one for the device description
and one for the device event data. hex data is without a 0x prefix.

Device Description Format
-------------------------

    # EVEMU 1.0
    # comments are lines with # as first character
    N: <device name>
    I: <bustype (hex)> <vendor (hex)> <product (hex)> <version (hex)>
     --- for each kernel property (2.3.38 only) ---
    P: <byte 0 (hex)> <byte 1 (hex)> ... <byte 7 (hex)>
    P: <byte 8 (hex)> ...
     --- for each index from 0 to EV_CNT ---
    B: <index (hex)> <byte 0 (hex)> <byte 1 (hex)> ... <byte 7 (hex)>
    B: <index (hex)> <byte 8 (hex)> ...
     --- for each absolute axis ---
    A: <index (hex)> <min> <max> <fuzz> <flat>

The first line is a special comment and taken to describe the file format
version. It is always comment character (#), space, "EVEMU", space, followed
by a numeric version number in the format major.minor.
If the line is missing, file format 1.0 is assumed.

minor version numbers are additions of new fields, or alterations of a
field.
major version numbers are large redesigns of the format

Current file format versions supported:
 * 1.0

Event Data Format
-----------------

    E: <sec>.<usec> <evtype (hex)> <evcode (hex)> <ev value>
where type, code and value are the respective fields of the
input_event struct defined in linux/input.h


Copyright
---------

 * Copyright (C) 2010 Henrik Rydberg <rydberg@euromail.se>
 * Copyright (C) 2010 Canonical Ltd.
