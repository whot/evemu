noinst_PROGRAMS = \
	evemu-echo

bin_PROGRAMS = \
	evemu-describe \
	evemu-device \
	evemu-record \
	evemu-play \
	evemu-event

AM_CPPFLAGS =-I$(top_srcdir)/src/

AM_LDFLAGS = $(top_builddir)/src/libevemu.la

evemu_describe_SOURCES = evemu-record.c find_event_devices.c find_event_devices.h
evemu_record_SOURCES = $(evemu_describe_SOURCES)

evemu_play_SOURCES = evemu-play.c
evemu_device_SOURCES = $(evemu_play_SOURCES)

evemu_event_CFLAGS = $(LIBEVDEV_CFLAGS)
evemu_event_LDADD = $(LIBEVDEV_LIBS)

# man page generation
if HAVE_DOCTOOLS
# actual man pages
man_pages_sources = evemu-describe.txt evemu-device.txt
# shadow man pages
man_pages_shadows = evemu-record.1 evemu-play.1 evemu-event.1

man_pages = $(man_pages_sources:.txt=.1) $(man_pages_shadows)

$(man_pages_shadows): $(man_pages_sources:.txt=.1)

SUFFIXES = .1 .txt .xml

.xml.1:
	$(AM_V_GEN)$(XMLTO) man $<

.txt.xml:
	$(AM_V_GEN)$(ASCIIDOC) -b docbook -d manpage -o $@ $<

EXTRA_DIST = $(man_pages_sources)
dist_man_MANS = $(man_pages)
CLEANFILES = $(dist_man_MANS)
MAINTAINERCLEANFILES = $(man_pages) *.xml
endif

# make sure manpages were built before running dist
dist-hook:
	@test -f $(distdir)/evemu-describe.1 || (\
		echo "******************************************************" && \
		echo "Couldn't find man pages, refusing make dist." && \
		echo "Install xmlto/asciidoc to build man pages for tarball." && \
		echo "******************************************************" && \
		test )
