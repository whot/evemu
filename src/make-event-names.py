#!/usr/bin/env python
# Parses linux/input.h scanning for #define KEY_FOO 134
# Prints a C header file that can be used as mapping table
#

import re

SOURCE_FILE = "/usr/include/linux/input.h"

class Bits(object):
	pass

prefixes = [
		"EV_",
		"REL_",
		"ABS_",
		"KEY_",
		"BTN_",
		"LED_",
		"SND_",
		"MSC_",
		"SW_",
		"FF_",
		"SYN_",
		"INPUT_PROP_",
]

blacklist = [
		"EV_VERSION"
]

def print_bits(bits, prefix):
	print "static const char * const %s_map[%s_MAX + 1] = {" % (prefix, prefix.upper())
	print "	[0 ... %s_MAX] = NULL," % prefix.upper()
	for val, name in getattr(bits, prefix).items():
		print "	[%s] = \"%s\"," % (name, name)
	print "};"
	print ""

def print_map(bits):
	print "static const char * const * const map[EV_MAX + 1] = {"
	print "	[0 ... EV_MAX] = NULL,"

	for prefix in prefixes:
		if prefix == "BTN_" or prefix == "EV_" or prefix == "INPUT_PROP_":
			continue
		print "	[EV_%s] = %s_map," % (prefix[:-1], prefix[:-1].lower())

	print "};"
	print ""

def print_mapping_table(bits):
	print "/* THIS FILE IS GENERATED, DO NOT EDIT */"
	print ""
	print "#ifndef EVENT_NAMES_H"
	print "#define EVENT_NAMES_H"
	print ""
	print "#define SYN_MAX 3 /* linux/input.h doesn't define that */"
	print ""

	for prefix in prefixes:
		if prefix == "BTN_":
			continue
		print_bits(bits, prefix[:-1].lower())

	print_map(bits)

	print "static const char * event_get_type_name(int type) {"
	print "	return ev_map[type];"
	print " }"
	print ""
	print "static const char * event_get_code_name(int type, int code) {"
	print "	return map[type] ? map[type][code] : NULL;"
	print "}"
	print ""
	print "#endif /* EVENT_NAMES_H */"

def parse_define(bits, line):
	m = re.match(r"^#define\s+(\w+)\s+(\w+)", line)
	if m == None:
		return

	name = m.group(1)

	if name in blacklist:
		return

	try:
		value = int(m.group(2), 0)
	except ValueError:
		return

	for prefix in prefixes:
		if not name.startswith(prefix):
			continue

		attrname = prefix[:-1].lower()
		if attrname == "btn":
			attrname = "key"

		if not hasattr(bits, attrname):
			setattr(bits, attrname, {})
		b = getattr(bits, attrname)
		b[value] = name

def parse(path):
	fp = open(path)

	bits = Bits()

	lines = fp.readlines()
	for line in lines:
		if not line.startswith("#define"):
			continue
		parse_define(bits, line)

	return bits

if __name__ == "__main__":
	bits = parse(SOURCE_FILE)
	print_mapping_table(bits)
