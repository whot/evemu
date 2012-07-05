#
# @file python/Makefile.am
# @brief automake recipe for the evemu Python bindings
#
# Copyright 2011 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.

nobase_python_PYTHON = \
	$(wildcard evemu/*.py)

check_SCRIPTS = evemu-test-runner

TESTS = $(check_SCRIPTS)

evemu-test-runner: evemu-test-runner.in Makefile
	$(AM_V_GEN)$(SED) \
	  -e 's,[@]builddir[@],$(builddir),g' \
	  -e 's,[@]top_builddir[@],$(top_builddir),g' \
	  -e 's,[@]srcdir[@],$(srcdir),g' \
	  -e 's,[@]python[@],$(PYTHON),g' \
	  $< >$@
	chmod +x $@

BUILT_SOURCES = evemu-test-runner
EXTRA_DIST =  evemu-test-runner.in $(wildcard evemu/test*)
CLEANFILES = $(BUILT_SOURCES)
