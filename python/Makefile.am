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

if BUILD_PYTHON_BINDINGS
python_sources = \
	evemu/__init__.py \
	evemu/base.py \
	evemu/const.py \
	evemu/exception.py

nobase_python_PYTHON = $(python_sources)

test_sources = \
	       evemu/testing/__init__.py \
	       evemu/testing/mocker.py \
	       evemu/testing/result.py \
	       evemu/testing/runner.py \
	       evemu/testing/testcase.py \
	       evemu/tests/__init__.py \
	       evemu/tests/test_base.py \
	       evemu/tests/test_device.py

if BUILD_TESTS
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
endif
endif

EXTRA_DIST =  evemu-test-runner.in $(test_sources)

python3_pyc = \
		evemu/__pycache__/ \
		evemu/testing/__pycache__ \
		evemu/tests/__pycache

python2_pyc = $(test_sources:.py=.pyc) $(python_sources:.py=.pyc)

CLEANFILES = $(BUILT_SOURCES) $(python2_pyc) $(python3_pyc)
