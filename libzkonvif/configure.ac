#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.63])
AC_INIT([FULL-PACKAGE-NAME], [VERSION], [BUG-REPORT-ADDRESS])
AM_INIT_AUTOMAKE("libzkonvif", "0.1")
AC_CONFIG_SRCDIR(src/zk_wsdd.cpp)
AC_CONFIG_HEADERS([config.h])

# Checks for programs.
AC_PROG_CXX
AC_PROG_CC
AC_PROG_MAKE_SET
AM_PROG_AR
AC_PROG_RANLIB
AC_PROG_LIBTOOL

AC_SUBST(GLOBAL_CXXFLAGS)
GLOBAL_CXXFLAGS='-DZONEKEY_SOURCE -DMAX_STACK=8192'

# Checks for libraries.
AC_CHECK_LIB(ssl, ssl2_enc_init, 
		[ GLOBAL_CXXFLAGS="${GLOBAL_CXXFLAGS}"  ], 
		[ echo "Warning: NO openssl lib!" ])

# Checks for header files.
AC_CHECK_HEADERS([openssl/ssl.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_C_INLINE
AC_TYPE_SIZE_T


# Checks for library functions.

AC_OUTPUT([ Makefile src/Makefile test/Makefile
		 ])
