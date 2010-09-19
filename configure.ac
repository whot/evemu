# Initialize Autoconf
AC_PREREQ([2.60])
AC_INIT([Kernel device emulation],
        [1.0.0],
        [],
        [utouch-evemu])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_AUX_DIR([config-aux])

# Initialize Automake
AM_INIT_AUTOMAKE([foreign dist-bzip2])
AM_MAINTAINER_MODE

LIB_VERSION=1:0:0
AC_SUBST([LIB_VERSION])

# Initialize libtool
AC_PROG_LIBTOOL

# Checks for programs.
AC_PROG_CC
AC_PROG_INSTALL

AC_CONFIG_FILES([Makefile
                 src/Makefile
                 tools/Makefile
                 utouch-evemu.pc])
AC_OUTPUT
