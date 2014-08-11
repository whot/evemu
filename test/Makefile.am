if BUILD_TESTS
noinst_PROGRAMS = test-c-compile test-cxx-compile test-evemu-create
TESTS = $(noinst_PROGRAMS)

AM_CPPFLAGS = -I$(top_srcdir)/src/

test_c_compile_SOURCES = test-c-compile.c
test_c_compile_LDADD = $(top_builddir)/src/libevemu.la

test_cxx_compile_SOURCES = test-cxx-compile.cpp
test_cxx_compile_LDADD = $(top_builddir)/src/libevemu.la

test_evemu_create_SOURCES = test-evemu-create.c
test_evemu_create_LDADD = $(top_builddir)/src/libevemu.la
test_evemu_create_LDFLAGS = -static
endif

CLEANFILES = evemu.tmp.*
