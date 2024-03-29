AC_INIT([enigma2],[3.0.0],[enigma2-devel@lists.elitedvb.net])
AM_INIT_AUTOMAKE([foreign dist-bzip2 no-define tar-pax -Wno-portability])
AC_CONFIG_HEADERS([enigma2_config.h])

# Silent rules are available since 1.11, but older versions
# are still in use. So don't use them unconditionally.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_USE_SYSTEM_EXTENSIONS
AC_SYS_LARGEFILE

AC_PROG_CC
AC_PROG_CXX
m4_ifdef([LT_INIT], [LT_INIT], [AC_PROG_LIBTOOL])
AC_CONFIG_MACRO_DIR([m4])
AC_OPENMP

AC_PATH_PROG(MSGFMT, msgfmt, AC_MSG_ERROR(Could not find msgfmt))
# AC_PATH_PROG(MSGINIT, msginit, AC_MSG_ERROR(Could not find msginit))
# AC_PATH_PROG(MSGMERGE, msgmerge, AC_MSG_ERROR(Could not find msgmerge))
# AC_PATH_PROG(MSGUNIQ, msguniq, AC_MSG_ERROR(Could not find msguniq))
# AC_PATH_PROG(XGETTEXT, xgettext, AC_MSG_ERROR(Could not find xgettext))

AM_PATH_PYTHON
AX_PYTHON_DEVEL
AX_PKG_SWIG
AX_SWIG_ENABLE_CXX
AX_SWIG_PYTHON
AX_PTHREAD

TUXBOX_APPS_DVB

AM_CONDITIONAL(HAVE_GIT_DIR, test -d "$srcdir/.git")
AM_CONDITIONAL(HAVE_FAKE_GIT_DIR, test -f "$srcdir/.git/last_commit_info")

dnl versions of gstreamer and plugins-base
AC_ARG_WITH(gstversion,
	AS_HELP_STRING([--with-gstversion],[use gstreamer version (major.minor)]),
	[GST_MAJORMINOR=$withval],[GST_MAJORMINOR=0.10])

PKG_CHECK_MODULES(BASE, [freetype2 fribidi gstreamer-$GST_MAJORMINOR gstreamer-pbutils-$GST_MAJORMINOR libdvbsi++ libpng libxml-2.0 sigc++-1.2 libssl libcrypto])
PKG_CHECK_MODULES(LIBDDVD, libdreamdvd, HAVE_LIBDDVD="yes", HAVE_LIBDDVD="no")
AM_CONDITIONAL(HAVE_LIBDDVD, test "$HAVE_LIBDDVD" = "yes")

AC_CHECK_LIB([dl], [dlopen], [LIBDL_LIBS="-ldl"], [AC_MSG_ERROR([Could not find libdl])])
AC_SUBST(LIBDL_LIBS)
AC_CHECK_LIB([jpeg], [jpeg_set_defaults], [LIBJPEG_LIBS="-ljpeg"], [AC_MSG_ERROR([Could not find libjpeg])])
AC_SUBST(LIBJPEG_LIBS)
AC_CHECK_LIB([ungif], [DGifOpen], [LIBGIF_LIBS="-lungif"], [AC_CHECK_LIB([gif], [DGifOpen], [LIBGIF_LIBS="-lgif"], [AC_MSG_ERROR([Could not find libgif or libungif])])])
AC_SUBST(LIBGIF_LIBS)

AC_LANG_PUSH([C++])
AC_CHECK_LIB([xmlccwrap], [exit], [LIBXMLCCWRAP_LIBS="-lxmlccwrap"], [AC_MSG_ERROR([Could not find libxmlccwrap])])
AC_SUBST(LIBXMLCCWRAP_LIBS)
AC_LANG_POP

AC_ARG_WITH(boxtype,
	[  --with-boxtype=NAME box type [[none,dm7025,dm800...]]],
	[BOXTYPE="$withval"],[BOXTYPE="dm800"])
AC_SUBST(BOXTYPE)
AC_DEFINE_UNQUOTED(BOXTYPE,"$BOXTYPE",[box type])

AM_CONDITIONAL(AZBOX, test `echo "$BOXTYPE" | cut -b 1-5` == "azbox")
AM_CONDITIONAL(CUBE, test `echo "$BOXTYPE" | cut -b 1-4` == "cube")
AM_CONDITIONAL(DAGS, test `echo "$BOXTYPE" | cut -b 1-4` == "dags")
AM_CONDITIONAL(DREAMBOX, test `echo "$BOXTYPE" | cut -b 1-2` == "dm")
AM_CONDITIONAL(VUPLUS, test `echo "$BOXTYPE" | cut -b 1-2` == "vu")
AM_CONDITIONAL(XTREND, test `echo "$BOXTYPE" | cut -b 1-2` == "et")
AM_CONDITIONAL(INI, test `echo "$BOXTYPE" | cut -b 1-3` == "ini")
AM_CONDITIONAL(GIGABLUE, test `echo "$BOXTYPE" | cut -b 1-2` == "gb")
AM_CONDITIONAL(ODIN, test `echo "$BOXTYPE" | cut -b 1-4` == "odin")
AM_CONDITIONAL(EBOX, test `echo "$BOXTYPE" | cut -b 1-4` == "ebox")
AM_CONDITIONAL(AZBOXHD, test "$BOXTYPE" == "azboxhd")
AM_CONDITIONAL(AZBOXME, test "$BOXTYPE" == "azboxme")
AM_CONDITIONAL(AZBOXMINIME, test "$BOXTYPE" == "azboxminime")
AM_CONDITIONAL(BLACKBOX7405, test "$BOXTYPE" == "blackbox7405")
AM_CONDITIONAL(CUBE, test "$BOXTYPE" == "cube")
AM_CONDITIONAL(DAGS1, test "$BOXTYPE" == "dags1")
AM_CONDITIONAL(DAGS2, test "$BOXTYPE" == "dags2")
AM_CONDITIONAL(DAGS3, test "$BOXTYPE" == "dags3")
AM_CONDITIONAL(DM500HD, test "$BOXTYPE" == "dm500hd")
AM_CONDITIONAL(DM500HDV2, test "$BOXTYPE" == "dm500hdv2")
AM_CONDITIONAL(DM800, test "$BOXTYPE" == "dm800")
AM_CONDITIONAL(DM800SE, test "$BOXTYPE" == "dm800se")
AM_CONDITIONAL(DM800SEV2, test "$BOXTYPE" == "dm800sev2")
AM_CONDITIONAL(DM7020HD, test "$BOXTYPE" == "dm7020hd")
AM_CONDITIONAL(DM7020HDV2, test "$BOXTYPE" == "dm7020hdv2")
AM_CONDITIONAL(DM8000, test "$BOXTYPE" == "dm8000")
AM_CONDITIONAL(E3HD, test "$BOXTYPE" == "e3hd")
AM_CONDITIONAL(EBOX5000, test "$BOXTYPE" == "ebox5000")
AM_CONDITIONAL(EBOX5100, test "$BOXTYPE" == "ebox5100")
AM_CONDITIONAL(EBOX7358, test "$BOXTYPE" == "ebox7358")
AM_CONDITIONAL(EBOXLUMI, test "$BOXTYPE" == "eboxlumi")
AM_CONDITIONAL(ET4X00, test "$BOXTYPE" == "et4x00")
AM_CONDITIONAL(ET5X00, test "$BOXTYPE" == "et5x00")
AM_CONDITIONAL(ET6X00, test "$BOXTYPE" == "et6x00")
AM_CONDITIONAL(ET9X00, test "$BOXTYPE" == "et9x00")
AM_CONDITIONAL(ET8000, test "$BOXTYPE" == "et8000")
AM_CONDITIONAL(ET10000, test "$BOXTYPE" == "et10000")
AM_CONDITIONAL(EW7358, test `echo "$BOXTYPE"` == "ew7358")
AM_CONDITIONAL(GB800SOLO, test "$BOXTYPE" == "gb800solo")
AM_CONDITIONAL(GB800SE, test "$BOXTYPE" == "gb800se")
AM_CONDITIONAL(GB800UE, test "$BOXTYPE" == "gb800ue")
AM_CONDITIONAL(GB800SEPLUS, test "$BOXTYPE" == "gb800seplus")
AM_CONDITIONAL(GB800UEPLUS, test "$BOXTYPE" == "gb800ueplus")
AM_CONDITIONAL(GBQUADPLUS, test "$BOXTYPE" == "gbquadplus")
AM_CONDITIONAL(GBQUAD, test "$BOXTYPE" == "gbquad")
AM_CONDITIONAL(INIHDE, test "$BOXTYPE" == "inihde")
AM_CONDITIONAL(INIHDP, test "$BOXTYPE" == "inihdp")
AM_CONDITIONAL(INIHDX, test "$BOXTYPE" == "inihdx")
AM_CONDITIONAL(IXUSSZERO, test "$BOXTYPE" == "ixusszero")
AM_CONDITIONAL(IXUSSONE, test "$BOXTYPE" == "ixussone")
AM_CONDITIONAL(ODINM6, test "$BOXTYPE" == odinm6)
AM_CONDITIONAL(ODINM7, test "$BOXTYPE" == odinm7)
AM_CONDITIONAL(ODINM9, test "$BOXTYPE" == odinm9)
AM_CONDITIONAL(VUUNO, test "$BOXTYPE" == vuuno)
AM_CONDITIONAL(VUULTIMO, test "$BOXTYPE" == vuultimo)
AM_CONDITIONAL(VUSOLO, test "$BOXTYPE" == vusolo)
AM_CONDITIONAL(VUDUO, test "$BOXTYPE" == vuduo)
AM_CONDITIONAL(VUSOLO2, test "$BOXTYPE" == vusolo2)
AM_CONDITIONAL(VUDUO2, test "$BOXTYPE" == vuduo2)
AM_CONDITIONAL(XP1000, test "$BOXTYPE" == xp1000)
AM_CONDITIONAL(HAVE_COLORLCD2, test "$BOXTYPE" == dm800se -o "$BOXTYPE" == dm800sev2)
AM_CONDITIONAL(HAVE_COLORLCD1, test "$BOXTYPE" == dm8000 -o "$BOXTYPE" == dm800 -o "$BOXTYPE" == dm7020hd -o "$BOXTYPE" == dm7020hdv2)

if test `echo "$BOXTYPE" | cut -b 1-2` == "dm"; then
	AC_DEFINE(DREAMBOX, 1, [Dreambox hardware])
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
fi

AC_ARG_WITH(nolcd,
	AS_HELP_STRING([--with-nolcd], [disable ascii based lcd, yes or no]),
	[[withnolcd=$withval]],
	[[withnolcd=no]]
)
if test x"$withnolcd" != xno ; then
	AC_DEFINE(NO_LCD, 1,[Define when disable an ascii based lcd device])
fi
AM_CONDITIONAL(NO_LCD, test x"$withnolcd" != xno)

AC_ARG_WITH(textlcd,
	AS_HELP_STRING([--with-textlcd], [use ascii based lcd, yes or no]),
	[[withtextlcd=$withval]],
	[[withtextlcd=no]]
)
if test x"$withtextlcd" != xno ; then
	AC_DEFINE(HAVE_TEXTLCD, 1,[Define when using an ascii based lcd device])
fi
AM_CONDITIONAL(HAVE_TEXTLCD, test x"$withtextlcd" != xno)

AC_ARG_WITH(colorlcd,
	AS_HELP_STRING([--with-colorlcd], [use 96x64 16bpp color display, yes or no]),
	[[withcolorlcd=$withval]],
	[[withcolorlcd=no]]
)
if test x"$withcolorlcd" != xno ; then
	AC_DEFINE(HAVE_COLORLCD, 1,[Define when using a 96x64 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD, test x"$withcolorlcd" != xno)

AC_ARG_WITH(colorlcd128,
	AS_HELP_STRING([--with-colorlcd128], [use 128x64 16bpp color display, yes or no]),
	[[withcolorlcd128=$withval]],
	[[withcolorlcd128=no]]
)
if test x"$withcolorlcd128" != xno ; then
	AC_DEFINE(HAVE_COLORLCD128, 1,[Define when using a 128x64 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD128, test x"$withcolorlcd" != xno)

AC_ARG_WITH(colorlcd220,
	AS_HELP_STRING([--with-colorlcd220], [use 220x176 16bpp color display, yes or no]),
	[[withcolorlcd220=$withval]],
	[[withcolorlcd220=no]]
)
if test x"$withcolorlcd220" != xno ; then
	AC_DEFINE(HAVE_COLORLCD220, 1,[Define when using a 220x176 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD220, test x"$withcolorlcd220" != xno)

AC_ARG_WITH(colorlcd400,
	AS_HELP_STRING([--with-colorlcd400], [use 400x240 16bpp color display, yes or no]),
	[[withcolorlcd400=$withval]],
	[[withcolorlcd400=no]]
)
if test x"$withcolorlcd400" != xno ; then
	AC_DEFINE(HAVE_COLORLCD400, 1,[Define when using a 400x240 color display device])
fi

AM_CONDITIONAL(HAVE_COLORLCD400, test x"$withcolorlcd400" != xno)

AC_ARG_WITH(bwlcd255,
	AS_HELP_STRING([--with-bwlcd255], [use 255x64 1bpp black and white display, yes or no]),
	[[withbwlcd255=$withval]],
	[[withbwlcd255=no]]
)
if test x"$withbwlcd255" != xno ; then
	AC_DEFINE(HAVE_BWLCD255, 1,[Define when using a 255x64 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD255, test x"$withbwlcd255" != xno)

AC_ARG_WITH(bwlcd140,
	AS_HELP_STRING([--with-bwlcd140], [use 140x32 1bpp black and white display, yes or no]),
	[[withbwlcd140=$withval]],
	[[withbwlcd140=no]]
)
if test x"$withbwlcd140" != xno ; then
	AC_DEFINE(HAVE_BWLCD140, 1,[Define when using a 140x32 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD140, test x"$withbwlcd140" != xno)

AC_ARG_WITH(bwlcd128,
	AS_HELP_STRING([--with-bwlcd128], [use 128x32 1bpp black and white display, yes or no]),
	[[withbwlcd128=$withval]],
	[[withbwlcd128=no]]
)
if test x"$withbwlcd128" != xno ; then
	AC_DEFINE(HAVE_BWLCD128, 1,[Define when using a 128x32 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD128, test x"$withbwlcd128" != xno)

AC_ARG_WITH(oldpvr,
	AS_HELP_STRING([--with-oldpvr], [use /dev/misc/pvr instead of /dev/dvb/adapterX/dvrX, yes or no]),
	[[witholdpvr=$withval]],
	[[witholdpvr=no]]
)
if test x"$witholdpvr" != xno ; then
	AC_DEFINE(HAVE_OLDPVR, 1,[Define when using /dev/misc/pvr])
fi
AM_CONDITIONAL(HAVE_OLDPVR, test x"$witholdpvr" != xno)

if test `echo "$BOXTYPE" | cut -b 1-2` == "et" ; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
fi

if test `echo "$BOXTYPE" | cut -b 1-4` == "odin"; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
fi

if test "$BOXTYPE" == "azboxme" -o "$BOXTYPE" == "azboxminime"; then
	AC_DEFINE(FORCE_ADVANCED_REMOTE, 1,[define to fixup the input device identification when the remote control is actually an 'advanced' remote (with play/forward/rewind keys)])
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
	AC_DEFINE(FORCE_NO_ACCELNEVER, 1,[define when the framebuffer acceleration auto not working correct])	
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(KEY_TV_TO_KEY_STOP, 1,[define when rc sends a KEY_TV event for its KEY_STOP])
	AC_DEFINE(KEY_VIDEO_TO_KEY_SUBTITLE, 1,[define when rc sends a KEY_VIDEO event for its KEY_SUBTITLE])
	AC_DEFINE(KEY_RADIO_TO_KEY_RECORD, 1,[define when rc sends a KEY_RADIO event for its KEY_RECORD])
	AC_DEFINE(KEY_HOME_TO_KEY_OPEN, 1,[define when rc sends a KEY_HOME event for its KEY_OPEN])
fi

if test "$BOXTYPE" == "azboxhd"; then
	AC_DEFINE(FORCE_ADVANCED_REMOTE, 1,[define to fixup the input device identification when the remote control is actually an 'advanced' remote (with play/forward/rewind keys)])
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
	AC_DEFINE(FORCE_NO_ACCELNEVER, 1,[define when the framebuffer acceleration auto not working correct])
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(KEY_HOME_TO_KEY_OPEN, 1,[define when rc sends a KEY_HOME event for its KEY_OPEN])
	AC_DEFINE(KEY_VIDEO_TO_KEY_EPG, 1,[define when rc sends a KEY_VIDEO event for its KEY_EPG])
	AC_DEFINE(KEY_TV_TO_KEY_MODE, 1,[define when rc sends a KEY_TV event for its KEY_MODE key])
	AC_DEFINE(KEY_TEXT_TO_KEY_AUDIO, 1,[define when rc sends a KEY_TEXT event for its KEY_AUDIO key])	
fi

if test "$BOXTYPE" == "ebox5000" -o "$BOXTYPE" == "ebox7358" -o "$BOXTYPE" == "ebox5100" -o "$BOXTYPE" == "eboxlumi"; then
	AC_DEFINE(KEY_SCREEN_TO_KEY_ANGLE, 1,[define when rc sends a KEY_SCREEN event for its KEY_ANGLE key])
	AC_DEFINE(KEY_TIME_TO_KEY_SLEEP, 1,[define when rc sends a KEY_TIME event for its KEY_SLEEP])
fi

if test `echo "$BOXTYPE" | cut -b 1-2` == "et" ; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
fi

if test `echo "$BOXTYPE" | cut -b 1-4` == "odin"; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
fi

if test `echo "$BOXTYPE" | cut -b 1-2` == "vu"; then
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
	AC_DEFINE(FORCE_ADVANCED_REMOTE, 1,[define to fixup the input device identification when the remote control is actually an 'advanced' remote (with play/forward/rewind keys)])
fi

if test `echo "$BOXTYPE" | cut -b 1-2` == "gb"; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
fi

if test `echo "$BOXTYPE" | cut -b 1-3` == "ini"; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
fi

if test `echo "$BOXTYPE" | cut -b 1-4` == "dags"; then
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
	AC_DEFINE(FORCE_ADVANCED_REMOTE, 1,[define to fixup the input device identification when the remote control is actually an 'advanced' remote (with play/forward/rewind keys)])
fi

if test "$BOXTYPE" == "sogno8800hd"; then
	AC_DEFINE(FORCE_ADVANCED_REMOTE, 1,[define to fixup the input device identification when the remote control is actually an 'advanced' remote (with play/forward/rewind keys)])
	AC_DEFINE(KEY_PLAY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(KEY_MEDIA_TO_KEY_BOOKMARKS, 1,[define when rc sends a KEY_MEDIA event for its KEY_BOOKMARKS key])
fi


AC_ARG_WITH(libsdl,
	AS_HELP_STRING([--with-libsdl],[use libsdl, yes or no]),
	[with_libsdl=$withval],[with_libsdl=no])
if test "$with_libsdl" = "yes"; then
	PKG_CHECK_MODULES(LIBSDL, sdl)
fi
AM_CONDITIONAL(HAVE_LIBSDL, test "$with_libsdl" = "yes")

AC_ARG_WITH(libxine,
	AS_HELP_STRING([--with-libxine],[use libxine, yes or no]),
	[with_libxine=$withval],[with_libxine=no])
if test "$with_libxine" = "yes"; then
	PKG_CHECK_MODULES(LIBXINE, libxine)
	AC_DEFINE([WITH_XINE],[1],[Define to 1 if you have libxine])
fi
AM_CONDITIONAL(HAVE_LIBXINE, test "$with_libxine" = "yes")

AC_ARG_WITH(debug,
	AS_HELP_STRING([--without-debug],[disable debugging code]),
	[with_debug="$withval"],[with_debug="yes"])
if test "$with_debug" = "yes"; then
	DEBUG_CFLAGS="-ggdb3"
	AC_DEFINE([DEBUG],[1],[Define to 1 to enable debugging code])
fi

AC_ARG_WITH(memcheck,
	AS_HELP_STRING([--with-memcheck],[enable memory leak checks]),
	[with_memcheck="$withval"],[with_memcheck="no"])
if test "$with_memcheck" = "yes"; then
	AC_DEFINE([MEMLEAK_CHECK],[1],[Define to 1 to enable memory leak checks])
fi

AC_ARG_WITH(po,
	AS_HELP_STRING([--with-po],[enable updating of po files]),
	[with_po="$withval"],[with_po="no"])
if test "$with_po" = "yes"; then
	AC_PATH_PROG(MSGINIT, msginit, AC_MSG_ERROR(Could not find msginit))
	AC_PATH_PROG(MSGMERGE, msgmerge, AC_MSG_ERROR(Could not find msgmerge))
	AC_PATH_PROG(MSGUNIQ, msguniq, AC_MSG_ERROR(Could not find msguniq))
	AC_PATH_PROG(XGETTEXT, xgettext, AC_MSG_ERROR(Could not find xgettext))
	if test -z "$MSGINIT" -o -z "$MSGMERGE" -o -z "$MSGUNIQ" -o -z "$XGETTEXT"; then
		AC_MSG_ERROR([Could not find required gettext tools])
	fi
fi
AM_CONDITIONAL(UPDATE_PO, test "$with_po" = "no")

ENIGMA2_CFLAGS="-fno-rtti -fno-exceptions"
AC_SUBST(ENIGMA2_CFLAGS)

CPPFLAGS="$CPPFLAGS $PYTHON_CPPFLAGS"
CFLAGS="$CFLAGS $DEBUG_CFLAGS -Wall -Wno-deprecated"
CXXFLAGS="$CXXFLAGS $DEBUG_CFLAGS -Wall -Wno-deprecated $BASE_CFLAGS $ENIGMA2_CFLAGS $PTHREAD_CFLAGS $OPENMP_CFLAGS"

AC_CONFIG_FILES([
Makefile
data/Makefile
data/fonts/Makefile
data/extensions/Makefile
data/keymaps/Makefile
data/defaults/Makefile
data/displaytext/Makefile
data/display96/Makefile
data/display128/Makefile
data/display220/Makefile
data/display400/Makefile
data/vfd128/Makefile
data/vfd140/Makefile
data/vfd255/Makefile
data/spinner/Makefile
include/Makefile
lib/Makefile
lib/base/eenv.cpp
lib/python/Makefile
lib/python/Components/Makefile
lib/python/Components/Converter/Makefile
lib/python/Components/Renderer/Makefile
lib/python/Components/Sources/Makefile
lib/python/Screens/Makefile
lib/python/Plugins/Makefile
lib/python/Plugins/Extensions/Makefile
lib/python/Plugins/Extensions/CutListEditor/Makefile
lib/python/Plugins/Extensions/CutListEditor/meta/Makefile
lib/python/Plugins/Extensions/DVDBurn/Makefile
lib/python/Plugins/Extensions/DVDBurn/meta/Makefile
lib/python/Plugins/Extensions/DVDPlayer/Makefile
lib/python/Plugins/Extensions/DVDPlayer/meta/Makefile
lib/python/Plugins/Extensions/MediaScanner/Makefile
lib/python/Plugins/Extensions/MediaScanner/meta/Makefile
lib/python/Plugins/Extensions/MediaPlayer/Makefile
lib/python/Plugins/Extensions/MediaPlayer/meta/Makefile
lib/python/Plugins/Extensions/Modem/Makefile
lib/python/Plugins/Extensions/PicturePlayer/Makefile
lib/python/Plugins/Extensions/PicturePlayer/meta/Makefile
lib/python/Plugins/Extensions/PicturePlayer/data/Makefile
lib/python/Plugins/Extensions/SocketMMI/Makefile
lib/python/Plugins/Extensions/SocketMMI/meta/Makefile
lib/python/Plugins/Extensions/SocketMMI/src/Makefile
lib/python/Plugins/Extensions/TuxboxPlugins/Makefile
lib/python/Plugins/Extensions/TuxboxPlugins/meta/Makefile
lib/python/Plugins/Extensions/AccuWeather/Makefile
lib/python/Plugins/Extensions/AccuWeather/acuwheathericons/Makefile
lib/python/Plugins/Extensions/AccuWeather/image/Makefile
lib/python/Plugins/Extensions/AccuWeather/locale/Makefile
lib/python/Plugins/Extensions/AccuWeather/locale/es/Makefile
lib/python/Plugins/Extensions/AccuWeather/locale/es/LC_MESSAGES/Makefile
lib/python/Plugins/Extensions/AccuWeather/wheathericons/Makefile
lib/python/Plugins/Extensions/AccuWeather/xbmcweather/Makefile
lib/python/Plugins/Extensions/AccuWeather/xbmcweather/small/Makefile
lib/python/Plugins/Extensions/IniGmailReader/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/lib/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/lib/biplist/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/mediabackends/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/Skins/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/Skins/Classic/Makefile
lib/python/Plugins/Extensions/IniAirPlayer/Skins/Classic/1280x720/Makefile
lib/python/Plugins/Extensions/IniEcasa/Makefile
lib/python/Plugins/Extensions/IniWebcamViewer/Makefile
lib/python/Plugins/Extensions/IniHbbTV/Makefile
lib/python/Plugins/Extensions/IniMyTube/Makefile
lib/python/Plugins/Extensions/IniZapHistoryBrowser/Makefile
lib/python/Plugins/Extensions/IniLastFM/Makefile
lib/python/Plugins/Extensions/IniSHOUTcast/Makefile
lib/python/Plugins/Extensions/FileCommander/Makefile
lib/python/Plugins/Extensions/FileCommander/addons/Makefile
lib/python/Plugins/Extensions/FileCommander/pic/Makefile
lib/python/Plugins/Extensions/FileCommander/images/Makefile
lib/python/Plugins/SystemPlugins/Makefile
lib/python/Plugins/SystemPlugins/IceTV/Makefile
lib/python/Plugins/SystemPlugins/CableScan/Makefile
lib/python/Plugins/SystemPlugins/CommonInterfaceAssignment/Makefile
lib/python/Plugins/SystemPlugins/CommonInterfaceAssignment/meta/Makefile
lib/python/Plugins/SystemPlugins/DiseqcTester/Makefile
lib/python/Plugins/SystemPlugins/DiseqcTester/meta/Makefile
lib/python/Plugins/SystemPlugins/FastScan/Makefile
lib/python/Plugins/SystemPlugins/FastScan/xml/Makefile
lib/python/Plugins/SystemPlugins/HdmiCEC/Makefile
lib/python/Plugins/SystemPlugins/Hotplug/Makefile
lib/python/Plugins/SystemPlugins/Hotplug/meta/Makefile
lib/python/Plugins/SystemPlugins/NetworkWizard/Makefile
lib/python/Plugins/SystemPlugins/NetworkWizard/meta/Makefile
lib/python/Plugins/SystemPlugins/PositionerSetup/Makefile
lib/python/Plugins/SystemPlugins/PositionerSetup/meta/Makefile
lib/python/Plugins/SystemPlugins/SABnzbdSetup/Makefile
lib/python/Plugins/SystemPlugins/SatelliteEquipmentControl/Makefile
lib/python/Plugins/SystemPlugins/SatelliteEquipmentControl/meta/Makefile
lib/python/Plugins/SystemPlugins/Satfinder/Makefile
lib/python/Plugins/SystemPlugins/Satfinder/meta/Makefile
lib/python/Plugins/SystemPlugins/SoftwareManager/Makefile
lib/python/Plugins/SystemPlugins/SoftwareManager/meta/Makefile
lib/python/Plugins/SystemPlugins/VideoClippingSetup/Makefile
lib/python/Plugins/SystemPlugins/VideoEnhancement/Makefile
lib/python/Plugins/SystemPlugins/VideoEnhancement/meta/Makefile
lib/python/Plugins/SystemPlugins/VideoTune/Makefile
lib/python/Plugins/SystemPlugins/VideoTune/meta/Makefile
lib/python/Plugins/SystemPlugins/WirelessLan/Makefile
lib/python/Plugins/SystemPlugins/WirelessLan/meta/Makefile
lib/python/Plugins/SystemPlugins/IniLCNScanner/Makefile
lib/python/Tools/Makefile
po/Makefile
main/Makefile
tools/Makefile
tools/enigma2.sh
enigma2.pc
])
AC_OUTPUT
