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
	evemu.c \
	evemu.h \
	version.h

libevemuincludedir = $(includedir)
libevemuinclude_HEADERS = evemu.h

event-names.h: Makefile make-event-names.py
	$(srcdir)/make-event-names.py --output=c > $@

event_names.py: Makefile make-event-names.py
	$(srcdir)/make-event-names.py --output=python > $@

EXTRA_DIST = $(version_script) make-event-names.py convert-old-dumps-to-1.1.py
CLEANFILES = event-names.h event_names.py event_names.pyc
BUILT_SOURCES = event-names.h event_names.py
