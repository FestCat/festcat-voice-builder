# Copyright (C) 2012  Sergio Oller <sergioller@gmail.com>
#
#  This script is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation,
#  version 2.1 of the License.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


# AC_INIT (package, version, [bug-report], [tarname], [url])
AC_INIT([!VOICENAME!], [3.0],https://github.com/FestCat/festcat-voice-builder/issues,!VOICENAME!,[http://www.talp.cat/festcat])
AC_PREREQ([2.59])
AC_PROG_SED
AC_PROG_GREP
AC_PROG_AWK
AC_PROG_INSTALL
AC_PROG_MKDIR_P


# Checks for Festival: Required to install.
AC_ARG_ENABLE(festivalpath,AS_HELP_STRING([--enable-festivalpath],[--enable-festivalpath=/path/to/festival (specify a custom festival path)]),[festivalpath=$enableval])

if test -d "${festivalpath}"; then 
    echo "using custom festival path: $festivalpath"
else
    festivalpath="$PATH"
fi

# FESTIVALBIN
AC_PATH_PROG([FESTIVALBIN], [festival], [:], [${festivalpath}])

if test ! -f "${FESTIVALBIN}"; then
        AC_MSG_ERROR(Can't find festival)
fi


# Checks for libdir and datadir
${FESTIVALBIN} --pipe > /dev/null 2>&1 << EOF
(set! fp (fopen "datadir.txt" "w"))
(if (boundp 'datadir)
(format fp datadir)
(format fp libdir)
)
(fclose fp)
EOF

FESTDATADIR=`cat "datadir.txt"`
rm "datadir.txt"

if test ! -d "${FESTDATADIR}"; then
        AC_MSG_ERROR(Can't find neither datadir or libdir)
fi
echo "Festival data directory: ${FESTDATADIR} found."

VOICENAME=!VOICENAME!

AC_SUBST(FESTDATADIR)
AC_SUBST(VOICENAME)

AC_CONFIG_FILES([Makefile])

AC_OUTPUT

