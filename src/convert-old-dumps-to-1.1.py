#!/bin/env python
# -*- coding: utf-8 -*-
#
# Parses evemu files with format 1.0 and outputs evemu format 1.1.
# Command line:
#   export PYTHONPATH=/path/to/evemu/python
#   python convert-old-dumps-to-1.1.py myEvent.desc [myEvent.events]
#

# Make sure the print statement is disabled and the function is used.
from __future__ import print_function

import os
import re
import sys

import evemu

def usage(args):
	print("%s mydev.desc [mydev.events]" % os.path.basename(args[0]))
	return 1

if __name__ == "__main__":
	if len(sys.argv) < 2:
		exit(usage(sys.argv))
	file_desc = sys.argv[1]
	d = evemu.Device(file_desc, create=False)
	d.describe(sys.stdout)
	if len(sys.argv) > 2:
		with open(sys.argv[2]) as f:
			for e in d.events(f):
				print(e)
