installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn Modem \
	IniMyTube IniSHOUTcast IniLastFM IniZapHistoryBrowser AccuWeather IniGmailReader IniHbbTV IniAirPlayer FileCommander \
	IniEcasa IniWebcamViewer

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

install_PYTHON = __init__.py
