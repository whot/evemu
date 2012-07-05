version_script = $(srcdir)/libevemu.ver

lib_LTLIBRARIES = libevemu.la

libevemu_la_LDFLAGS = \
	-version-info @LIB_VERSION@ \
	-Wl,-z,defs -Wl,--as-needed \
	-Wl,--version-script=$(version_script)

libevemu_la_CFLAGS = \
	-Wno-format

libevemu_la_SOURCES = \
	evemu-impl.h \
	evemu.c

INCLUDES = -I$(top_srcdir)/include/

libevemuincludedir = $(includedir)
libevemuinclude_HEADERS = \
	$(top_srcdir)/include/evemu.h

EXTRA_DIST = $(version_script)

