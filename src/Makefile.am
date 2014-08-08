version_script = $(srcdir)/libevemu.ver

lib_LTLIBRARIES = libevemu.la

libevemu_la_LDFLAGS = \
	-version-info @LIB_VERSION@ \
	-Wl,-z,defs -Wl,--as-needed \
	-Wl,--version-script=$(version_script)

libevemu_la_SOURCES = \
	evemu-impl.h \
	evemu.c \
	evemu.h \
	version.h

libevemu_la_LIBADD = $(LIBEVDEV_LIBS)

AM_CPPFLAGS = -I$(top_srcdir)/include/ $(LIBEVDEV_CFLAGS)

libevemuincludedir = $(includedir)
libevemuinclude_HEADERS = evemu.h

EXTRA_DIST = $(version_script) convert-old-dumps-to-1.1.py
