noinst_PROGRAMS = \
	evemu-echo

bin_PROGRAMS = \
	evemu-describe \
	evemu-device \
	evemu-record \
	evemu-play

INCLUDES=-I$(top_srcdir)/include/

evemu_describe_SOURCES = evemu-describe.c
evemu_describe_LDFLAGS = -L$(top_builddir)/src/.libs/ -levemu

evemu_echo_SOURCES = evemu-echo.c
evemu_echo_LDFLAGS = -L$(top_builddir)/src/.libs/ -levemu

evemu_device_SOURCES = evemu-device.c
evemu_device_LDFLAGS = -L$(top_builddir)/src/.libs/ -levemu

evemu_record_SOURCES = evemu-record.c
evemu_record_LDFLAGS = -L$(top_builddir)/src/.libs/ -levemu
evemu_play_SOURCES = evemu-play.c
evemu_play_LDFLAGS = -L$(top_builddir)/src/.libs/ -levemu
