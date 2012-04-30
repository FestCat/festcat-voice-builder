AC_INIT(festcat-voice-builder, 0.1, sergioller@gmail.com)
AC_PREREQ()
AC_PROG_MAKE_SET()
#package information
#program checks
# cc
AC_PROG_CC
# ln -s
AC_PROG_LN_S
# wget
AC_PATH_PROG([WGET], [wget], [/usr/bin], [$PATH:/usr/bin])
if test ! -f "$WGET"; then
	AC_MSG_ERROR(Can't find wget)
fi
AC_SUBST(WGET)

#library checks
#header file checks
#type checks
AC_TYPE_SIZE_T
#structure checks
#compiler characteristics checks
#library functions check
#system service checks

AC_ARG_VAR(htk_user,AS_HELP_STRING([htk_user=USERNAME],[specify the HTK website user name]))
AC_SUBST([htk_user])

AC_ARG_VAR(htk_password,AS_HELP_STRING([htk_password=PASSWORD],[specify the HTK website password]))
AC_SUBST([htk_password])

AC_SUBST(PWD)

WORKDIR=$PWD/work
AC_ARG_VAR(WORKDIR,AS_HELP_STRING([WORKDIR=/directory/to/work/on],[specify the directory to work on]))
AC_SUBST(WORKDIR)
AC_CONFIG_FILES(Makefile deps/Makefile data/en/Makefile)
AC_OUTPUT

