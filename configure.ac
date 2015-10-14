# Initialize Autoconf
AC_PREREQ([2.60])
AC_INIT([Kernel device emulation],
        [2.3.0],
        [],
        [evemu])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_AUX_DIR([config-aux])

# Initialize Automake
AM_INIT_AUTOMAKE([foreign dist-xz no-dist-gzip])
AM_SILENT_RULES([yes])
AM_MAINTAINER_MODE([enable])

# Before making a release, the LIB_VERSION string should be
# modified.
# The string is of the form C:R:A.
# - If interfaces have been changed or added, but binary compatibility has
#   been preserved, change to C+1:0:A+1
# - If binary compatibility has been broken (eg removed or changed interfaces)
#   change to C+1:0:0
# - If the interface is the same as the previous version, change to C:R+1:A
LIB_VERSION=3:0:0
AC_SUBST([LIB_VERSION])

# Initialize libtool
AC_PROG_LIBTOOL

# Checks for programs.
AC_PROG_CC
AC_PROG_CXX
AC_PROG_INSTALL
AC_PROG_MKDIR_P
AM_PATH_PYTHON([2.6])

PKG_CHECK_MODULES([LIBEVDEV], [libevdev >= 1.2.99.902])

# man page generation
AC_ARG_VAR([XMLTO], [Path to xmlto command])
AC_PATH_PROG([XMLTO], [xmlto])
AC_ARG_VAR([ASCIIDOC], [Path to asciidoc command])
AC_PATH_PROG([ASCIIDOC], [asciidoc])
AM_CONDITIONAL([HAVE_DOCTOOLS], [test "x$XMLTO" != "x" && test "x$ASCIIDOC" != "x"])
if test "x$XMLTO" = "x" || test "x$ASCIIDOC" = "x"; then
	AC_MSG_WARN([xmlto or asciidoc not found - cannot create man pages without it])
fi

AC_ARG_ENABLE([python-bindings],
	AS_HELP_STRING([--disable-python-bindings], [disable generation of python bindings]),
	[case "${enableval}" in
	  yes) python_bindings=yes ;;
	  no)  python_bindings=no ;;
	  *) AC_MSG_ERROR([bad value ${enableval} for --disable-python-bindings]) ;;
	esac],[python_bindings=yes])

AM_CONDITIONAL(BUILD_PYTHON_BINDINGS, [test "x$python_bindings" = "xyes"])

AC_ARG_ENABLE([tests],
	AS_HELP_STRING([--disable-tests], [disable building of tests]),
	[case "${enableval}" in
	  yes) enable_tests=yes ;;
	  no)  enable_tests=no ;;
	  *) AC_MSG_ERROR([bad value ${enableval} for --disable-tests]) ;;
	esac],[enable_tests=yes])

AM_CONDITIONAL(BUILD_TESTS, [test "x$enable_tests" = "xyes"])

AC_SUBST(AM_CFLAGS,
         "-Wall -Wextra")


AC_CONFIG_FILES([Makefile
                 src/Makefile
                 python/Makefile
                 tools/Makefile
                 test/Makefile
                 evemu.pc])
AC_OUTPUT
