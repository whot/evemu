#!/usr/bin/env python
# Parses linux/input.h scanning for #define KEY_FOO 134
# Prints a Python file that can be used as mapping table
#

# Make sure the print statement is disabled and the function is used.
from __future__ import print_function

import argparse
import re
import sys
import textwrap

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
		"EV_VERSION",
]

# These defines only work from string->value, not the other way round
oneway = [
		"BTN_MISC",
		"BTN_MOUSE",
		"BTN_JOYSTICK",
		"BTN_GAMEPAD",
		"BTN_DIGI",
		"BTN_WHEEL",
		"BTN_TRIGGER_HAPPY"
]

# As above, but input.h defines them as aliases instead of int values
aliases = {}

def p(s):
	print(textwrap.dedent(s))

def print_python_bits(bits, prefix):
	if  not hasattr(bits, prefix):
		return

	print("%s_map = {" % (prefix))
	for val, name in getattr(bits, prefix).items():
		if val in oneway:
			print("	\"%s\" : %d," % (val, name))
		else:
			print("	%d : \"%s\", \"%s\" : %d," % (val, name, name, val))

	for alias, mapping in aliases.items():
		if prefix == "key" and alias.lower().startswith("btn"):
			pass
		elif not alias.lower().startswith(prefix):
			continue
		for val, name in getattr(bits, prefix).items():
			if name == mapping:
				print("	\"%s\" : %d," % (alias, val))
				break

	print("}")
	print("")

def print_python_map(bits):
	print("map = {")

	for val, name in getattr(bits, "ev").items():
		name = name[3:]
		if name == "REP" or name == "PWR"  or name == "FF_STATUS"  or name == "MAX":
			continue
		print("	%d : %s_map," % (val, name.lower()))
		print("	\"EV_%s\" : %s_map," % (name, name.lower()))

	print("}")
	print("")

def print_python_mapping_table(bits):
	p("""# THIS FILE IS GENERATED, DO NOT EDIT")
	""")

	for prefix in prefixes:
		if prefix == "BTN_":
			continue
		print_python_bits(bits, prefix[:-1].lower())

	print_python_map(bits)

	p("""
	def event_get_type_name(type):
		return ev_map[type]


	def event_get_code_name(type, code):
		try:
			return map[type][code]
		except KeyError:
			return 'UNKNOWN'
	""")

def parse_define(bits, line):
	m = re.match(r"^#define\s+(\w+)\s+(\w+)", line)
	if m == None:
		return

	name = m.group(1)

	if name in blacklist:
		return
	if name.startswith("EVIOC"):
		return

	try:
		value = int(m.group(2), 0)
	except ValueError:
		aliases[name] = m.group(2)
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
		if name in oneway:
			b[name] = value
		else:
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
	print_python_mapping_table(bits)
