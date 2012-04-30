AC_INIT(festcat-voice-building, 0.1, sergioller@gmail.com)
AC_PREREQ()
AC_PREFIX_DEFAULT([$PWD/install])
AC_PROG_MAKE_SET()
#package information
#program checks
# wget
AC_PATH_PROG([WGET], [wget], [/usr/bin], [$PATH:/usr/bin])
if test ! -f "$WGET"; then
	AC_MSG_ERROR(Can't find wget)
fi
AC_SUBST(WGET)

#library checks
#header file checks
#type checks
#structure checks
#compiler characteristics checks
#library functions check
#system service checks

AC_ARG_VAR(htk_user,AS_HELP_STRING([htk_user=USERNAME],[specify the HTK website user name]))
AC_SUBST([htk_user])

AC_ARG_VAR(htk_password,AS_HELP_STRING([htk_password=PASSWORD],[specify the HTK website password]))
AC_SUBST([htk_password])

AC_CONFIG_FILES(Makefile deps/Makefile)
AC_OUTPUT

