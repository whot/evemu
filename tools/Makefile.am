noinst_PROGRAMS = \
	evemu-echo

bin_PROGRAMS = \
	evemu-describe \
	evemu-device \
	evemu-record \
	evemu-play \
	evemu-event

INCLUDES=-I$(top_srcdir)/include/

AM_LDFLAGS = $(top_builddir)/src/libevemu.la


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
