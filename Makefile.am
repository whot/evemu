SUBDIRS = src tools python test

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = evemu.pc

INCLUDES = $(top_srcdir)/include/

.PHONY: ChangeLog INSTALL
INSTALL:
	$(INSTALL_CMD)

EXTRA_DIST = data

ChangeLog:
	@if test -d ".bzr"; then \
	    cmd=bzr; \
	elif test -d ".git"; then \
	    cmd=git; \
	else \
	    cmd="echo could not generate change"; \
	fi; \
	$${cmd} log > ChangeLog;

dist-hook: ChangeLog INSTALL

DISTCLEANFILES = ChangeLog
