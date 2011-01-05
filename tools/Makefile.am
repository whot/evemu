noinst_PROGRAMS = \
	evemu-echo

bin_PROGRAMS = \
	evemu-describe \
	evemu-device \
	evemu-record \
	evemu-play

INCLUDES=-I$(top_srcdir)/include/

evemu_describe_LDFLAGS = -L$(top_builddir)/src/.libs/ -lutouch-evemu
evemu_echo_LDFLAGS = -L$(top_builddir)/src/.libs/ -lutouch-evemu
evemu_device_LDFLAGS = -L$(top_builddir)/src/.libs/ -lutouch-evemu
evemu_record_LDFLAGS = -L$(top_builddir)/src/.libs/ -lutouch-evemu
evemu_play_LDFLAGS = -L$(top_builddir)/src/.libs/ -lutouch-evemu
