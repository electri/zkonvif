#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.63])
AC_INIT([zkdm], [0.0.1], [sunkwei@gmail.com])
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([ptz/ptz.h])
AC_CONFIG_HEADERS([config.h])

AC_CANONICAL_HOST

# Checks for programs.
AC_PROG_CXX
AC_PROG_CC
AC_PROG_LIBTOOL

LT_INIT([win32-dll shared])
AC_LIBTOOL_WIN32_DLL


# Checks for libraries.

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h])
AC_CHECK_HEADERS([visca/libvisca.h])

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.


VISCA_EXT=../../3rd/libvisca-1.0.0/visca/libvisca_posix.c

PLATFORM=$(uname -r)

case "$host_os" in
	*mingw32*)
		LDFLAGS="${LDFLAGS} -lws2_32"
		;;

	arm*)
		CFLAGS= "${CFLAGS} -marm -DVK3344=1"
		;;
esac


AC_OUTPUT([
		Makefile
		ptz/Makefile
		zkutil/Makefile
		pong/Makefile
		])
