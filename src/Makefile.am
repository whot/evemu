lib_LTLIBRARIES = libevemu.la

libevemu_la_LDFLAGS = -version-info @LIB_VERSION@

libevemu_la_SOURCES = \
	evemu.c

AM_CFLAGS = $(CWARNFLAGS)

INCLUDES = -I$(top_srcdir)/include/

libevemuincludedir = $(includedir)
libevemuinclude_HEADERS = \
	$(top_srcdir)/include/evemu.h
