SUBDIRS = src tools python test

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = evemu.pc

AM_CPPFLAGS = -I $(top_srcdir)/include/

.PHONY: INSTALL
INSTALL:
	$(INSTALL_CMD)

EXTRA_DIST = data

dist-hook: INSTALL
