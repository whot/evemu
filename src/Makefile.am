version_script = $(srcdir)/libutouch-evemu.ver

lib_LTLIBRARIES = libutouch-evemu.la

libutouch_evemu_la_LDFLAGS = \
	-version-info @LIB_VERSION@ \
	-Wl,-z,defs -Wl,--as-needed \
	-Wl,--version-script=$(version_script)

libutouch_evemu_la_CFLAGS = \
	-Wno-format

libutouch_evemu_la_SOURCES = \
	evemu-impl.h \
	evemu.c

INCLUDES = -I$(top_srcdir)/include/

libutouch_evemuincludedir = $(includedir)
libutouch_evemuinclude_HEADERS = \
	$(top_srcdir)/include/evemu.h

EXTRA_DIST = $(version_script)

