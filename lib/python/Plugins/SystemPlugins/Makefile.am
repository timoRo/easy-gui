installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = SoftwareManager PositionerSetup Satfinder \
	VideoTune Hotplug \
	CommonInterfaceAssignment \
	HdmiCEC VideoClippingSetup \
	VideoEnhancement WirelessLan NetworkWizard \
	SABnzbdSetup FastScan SatelliteEquipmentControl DiseqcTester \
	IniLCNScanner IceTV

if VUSOLO2
SUBDIRS += CableScan
endif

if VUDUO2
SUBDIRS += CableScan
endif

if VUUNO
SUBDIRS += CableScan
endif

if VUULTIMO
SUBDIRS += CableScan
endif

install_PYTHON = __init__.py
