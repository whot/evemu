TESTS = test-c-compile test-cxx-compile

check_PROGRAMS = $(TESTS)

INCLUDES = -I$(top_srcdir)/include/

test_c_compile_SOURCES = test-c-compile.c
test_c_compile_LDADD = $(top_builddir)/src/libevemu.la

test_cxx_compile_SOURCES = test-cxx-compile.cpp
test_cxx_compile_LDADD = $(top_builddir)/src/libevemu.la
