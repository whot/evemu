SUBDIRS = src tools

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = evemu.pc

INCLUDES = $(top_srcdir)/include/

.PHONY: ChangeLog INSTALL
INSTALL:
	$(INSTALL_CMD)
ChangeLog:
	bzr log > ChangeLog

dist-hook: ChangeLog INSTALL
