#!/bin/env python
# -*- coding: utf-8 -*-
#
# Parses evemu files with format 1.0 and outputs evemu format 1.1.
# Command line:
#   python convert-old-dumps-to-1.1.py myEvent.desc [myEvent.events]
#

import re
import os
import sys
import evemu
from event_names import *

def convert_events(lines):
	event_re = re.compile(r"E: (\d+\.\d*) ([a-fA-f0-9]+) ([a-fA-f0-9]+) (-?\d*)\n")

	for line in lines:
		m = event_re.match(line)
		if m:
			t, type, code, value = m.groups()
			type = int(type, 16)
			code = int(code, 16)
			value = int(value, 0)
			print "E: %s %04x %04x %04d\t" % (t, type, code, value),
			desc = ""
			if type == ev_map["EV_SYN"]:
				if code == syn_map["SYN_MT_REPORT"]:
					print "# ++++++++++++ %s (%d) ++++++++++" % (event_get_code_name(type, code), value)
				else:
					print "# ------------ %s (%d) ----------" % (event_get_code_name(type, code), value)
			else:
				print "# %s / %-20s %d" % ( event_get_type_name(type), event_get_code_name(type, code), value)
		else:
			print line,

def usage(args):
	print "%s mydev.desc [mydev.events]" % os.path.basename(args[0])
	return 1


if __name__ == "__main__":
	if len(sys.argv) < 2:
		exit(usage(sys.argv))
	file_desc = sys.argv[1]
	d = evemu.Device(file_desc)
	d.describe(sys.stdout)
	d = None
	if len(sys.argv) > 2:
		print "################################"
		print "#      Waiting for events      #"
		print "################################"
		with open(sys.argv[2]) as f:
			convert_events(f.readlines())
