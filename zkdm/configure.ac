#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([zkdm], [0.0.1], [sunkwei@gmail.com])
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([ptz/ptz.h])
AC_CONFIG_HEADERS([config.h])

# Checks for programs.
AC_PROG_CXX
AC_PROG_CC
AC_PROG_LIBTOOL

LT_INIT([dlopen win32-dll shared])

# Checks for libraries.

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h])
AC_CHECK_HEADERS([visca/libvisca.h])

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

AC_OUTPUT([
		Makefile
		ptz/Makefile
		])
