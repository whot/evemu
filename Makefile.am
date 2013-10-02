SUBDIRS = src tools python test

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = evemu.pc

.PHONY: INSTALL
INSTALL:
	$(INSTALL_CMD)

EXTRA_DIST = data

dist-hook: INSTALL
