# Initialize Autoconf
AC_PREREQ([2.60])
AC_INIT([Kernel device emulation],
        [1.0.9],
        [],
        [evemu])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_AUX_DIR([config-aux])

# Initialize Automake
AM_INIT_AUTOMAKE([foreign dist-xz])
AM_SILENT_RULES([yes])
AM_MAINTAINER_MODE([enable])

LIB_VERSION=1:0:0
AC_SUBST([LIB_VERSION])

# Initialize libtool
AC_PROG_LIBTOOL

# Checks for programs.
AC_PROG_CC
AC_PROG_CXX
AC_PROG_INSTALL
AM_PATH_PYTHON([2.6])

# man page generation
AC_ARG_VAR([XMLTO], [Path to xmlto command])
AC_PATH_PROG([XMLTO], [xmlto])
AC_ARG_VAR([ASCIIDOC], [Path to asciidoc command])
AC_PATH_PROG([ASCIIDOC], [asciidoc])
AM_CONDITIONAL([HAVE_DOCTOOLS], [test "x$XMLTO" != "x" && test "x$ASCIIDOC" != "x"])
if test "x$XMLTO" = "x" || test "x$ASCIIDOC" = "x"; then
	AC_MSG_WARN([xmlto or asciidoc not found - cannot create man pages without it])
fi

AC_SUBST(AM_CFLAGS,
         "-Wall -Wextra -pedantic -Werror -std=gnu99 -D_GNU_SOURCE=1")


AC_CONFIG_FILES([Makefile
                 src/Makefile
                 python/Makefile
                 tools/Makefile
                 test/Makefile
                 evemu.pc])
AC_OUTPUT
