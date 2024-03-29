#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from Plugins.Plugin import PluginDescriptor
# Components
from Components.config import config, ConfigSubList, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, getConfigListEntry, ConfigSelection, NoSave, ConfigNothing
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.FileTransfer import FileTransferJob
from Components.Task import job_manager
from Components.ActionMap import ActionMap
from Components.Scanner import openFile
from Components.MenuList import MenuList
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.StaticText import StaticText

# Screens
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import MovieLocationBox
from Screens.HelpMenu import HelpableScreen
from Screens.TaskList import TaskListScreen
from Screens.InfoBar import MoviePlayer as Movie_Audio_Player
# Tools
from Tools.Directories import *
from Tools.BoundFunction import boundFunction
# Various
from Plugins.Extensions.FileCommander.InputBoxmod import InputBox
from Plugins.Extensions.FileCommander.InputBoxmod import InputBoxmod
from os.path import isdir as os_path_isdir
from mimetypes import guess_type
from enigma import eServiceReference, eServiceCenter, eTimer, eSize, ePicLoad, getDesktop, eConsoleAppContainer, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from os import listdir, remove, rename, system, path, symlink, chdir
from os import system as os_system
from os import walk as os_walk
import os

EXTENSIONS = {
	".m4a" : "music",
	".mp2" : "music",
	".mp3" : "music",
	".wav" : "music",
	".ogg" : "music",
	".flac": "music",
	".ts"  : "movie",
	".avi" : "movie",
	".divx": "movie",
	".m4v" : "movie",
	".mpg" : "movie",
	".mpeg": "movie",
	".mkv" : "movie",
	".mp4" : "movie",
	".mov" : "movie",
	".m2ts": "movie",
	".wmv" : "movie",
	".jpg" : "picture",
	".jpeg": "picture",
	".png" : "picture",
	".bmp" : "picture",
	".m3u" : "stream",
	".m3u8": "stream",
}

##################################

pname = _("File Commander - Addon Mediaplayer")
pdesc = _("play/show Files")
pversion = "1.0-r0"

### play with movieplayer ###
class MoviePlayer(Movie_Audio_Player):
	def __init__(self, session, service):
		self.session = session
		self.WithoutStopClose = False
		Movie_Audio_Player.__init__(self, self.session, service)

	def leavePlayer(self):
		self.is_closing = True
		self.close()

	def leavePlayerConfirmed(self, answer):
		pass

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		self.leavePlayer()

	def showMovies(self):
		self.WithoutStopClose = True
		self.close()

	def movieSelected(self, service):
		self.leavePlayer(self.de_instance)

	def __onClose(self):
		if not(self.WithoutStopClose):
			self.session.nav.playService(self.lastservice)

### File viewer/line editor ###
class vEditor(Screen):

	skin = """
		<screen position="40,80" size="1200,600" title="">
			<widget name="list_head" position="10,10" size="1170,45" font="Regular;20" foregroundColor="#00fff000"/>
			<widget name="filedata"  scrollbarMode="showOnDemand" position="10,60" size="1160,500" itemHeight="25"/>
			<widget name="key_red" position="100,570" size="260,25" transparent="1" font="Regular;20"/>
			<widget name="key_green" position="395,570" size="260,25"  transparent="1" font="Regular;20"/>
			<widget name="key_yellow" position="690,570" size="260,25" transparent="1" font="Regular;20"/>
			<widget name="key_blue" position="985,570" size="260,25" transparent="1" font="Regular;20"/>
			<ePixmap position="70,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	def __init__(self, session, file):
		pname = _("File Commander - Addon File-Viewer")
		self.skin = vEditor.skin
		Screen.__init__(self, session)
		self.session = session
		self.file_name = file
		self.list = []
		self["filedata"] = MenuList(self.list)
		self["actions"] = ActionMap(["WizardActions", "ColorActions", "InfobarChannelSelection"],
		{
			"ok": self.editLine,
			"green": self.editLine,
			"back": self.exitEditor,
			"red": self.exitEditor,
			"yellow": self.del_Line,
			"blue": self.ins_Line,
			"showFavourites": self.posStart,
			"openServiceList": self.posEnd
		}, -1)
		self["list_head"] = Label(self.file_name)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Edit"))
		self["key_yellow"] = Label(_("Delete"))
		self["key_blue"] = Label(_("Insert"))
		self.selLine = None
		self.oldLine = None
		self.isChanged = False
		self.GetFileData(file)
		self.setTitle(pname)

	def exitEditor(self):
		if self.isChanged:
			warningtext = "\n" + (_("has been CHANGED! Do you want to save it?"))
			warningtext = warningtext + "\n\n" + (_("WARNING!"))
			warningtext = warningtext + "\n" + (_("The authors are NOT RESPONSIBLE"))
			warningtext = warningtext + "\n" + (_("for DATA LOST OR DISORDERS !!!"))
			msg = self.session.openWithCallback(self.SaveFile, MessageBox,_(self.file_name+self.file_name+warningtext), MessageBox.TYPE_YESNO)
			msg.setTitle(_("File Commander"))
		else:
			self.close()

	def GetFileData(self, fx):
		try:
			flines = open(fx, "r")
			zeile = 1
			for line in flines:
				self.list.append(str(zeile).zfill(4) + ": " + line)
				zeile += 1
			flines.close()
			self["list_head"] = Label(fx)
		except:
			pass

	def editLine(self):
		try:
			self.findtab = -1
			length = 95
			self.selLine = self["filedata"].getSelectionIndex()
			self.oldLine = self.list[self.selLine]
			my_editableText = self.list[self.selLine][:-1]
			editableText = my_editableText.partition(": ")[2]
#			os.system('echo %s %s >> /tmp/test.log' % ("oldline_a :", str(len(editableText))))
			if len(editableText) == 0:
				editableText = "" #self.list[self.selLine][:-1]
			self.findtab = editableText.find("\t", 0, len(editableText))
			if self.findtab != -1:
				editableText = editableText.replace("\t","        ")
			self.session.openWithCallback(self.callbackEditLine, InputBoxmod, title=_(_("original")+": "+editableText), visible_width=length, overwrite=False, firstpos_end=True, allmarked=False, windowTitle=_("Edit line ")+str(self.selLine+1), text=editableText)
		except:
			msg = self.session.open(MessageBox, _("This line is not editable!"), MessageBox.TYPE_ERROR)
			msg.setTitle(_("Error..."))

	def callbackEditLine(self, newline):
		if newline is not None:
			k = 0
			for x in self.list:
				if x == self.oldLine:
					if k == self.selLine:
						self.isChanged = True
						if self.findtab != -1:
							newline = newline.replace("        ", "\t")
							self.findtab = -1
						my_zeile = self.oldLine.partition(": ")[0]
						if self.oldLine.find(": ") != -1:
							newline = my_zeile + ": " + newline
						else:
							newline = "0000" + ": " + newline
						self.list.remove(x)
						self.list.insert(self.selLine, newline+'\n')
				k += 1
		self.findtab = -1
		self.selLine = None
		self.oldLine = None

	def posStart(self):
		self.selLine = 0
		self["filedata"].moveToIndex(0)

	def posEnd(self):
		self.selLine = len(self.list)
		self["filedata"].moveToIndex(len(self.list)-1)

	def del_Line(self):
		self.selLine = self["filedata"].getSelectionIndex()
		if len(self.list) > 1:
			self.isChanged = True
			del self.list[self.selLine]
			self.refreshList() 

	def ins_Line(self):
		self.selLine = self["filedata"].getSelectionIndex()
		self.list.insert(self.selLine, "0000: "+""+'\n')
		self.isChanged = True
		self.refreshList()

	def refreshList(self):
		zeile = 1
		for x in self.list:
			my_x = x.partition(": ")[2]
			self.list.remove(x)
			self.list.insert(zeile-1, str(zeile).zfill(4) + ": " + my_x) #'\n')
			zeile += 1
		self["filedata"].setList(self.list)

	def SaveFile(self, answer):
		if answer is True:
			try:
				if fileExists(self.file_name):
					system("cp " + self.file_name + " " + self.file_name + ".bak")
				eFile = open(self.file_name, "w")
				for x in self.list:
					my_x = x.partition(": ")[2]
					eFile.writelines(my_x)
				eFile.close()
			except:
				pass
			self.close()
		else:
			self.close()

class ImageViewer(Screen):
	s, w, h = 30, getDesktop(0).size().width(), getDesktop(0).size().height()
	skin = """
		<screen position="0,0" size="%d,%d" flags="wfNoBorder">
			<eLabel position="0,0" zPosition="0" size="%d,%d" backgroundColor="#00000000" />
			<widget name="image" position="%d,%d" size="%d,%d" zPosition="1" alphatest="on" />
			<widget name="status" position="%d,%d" size="20,20" zPosition="2" pixmap="skin_default/icons/record.png" alphatest="on" />
			<widget name="icon" position="%d,%d" size="20,20" zPosition="2" pixmap="skin_default/icons/ico_mp_play.png"  alphatest="on" />
			<widget source="message" render="Label" position="%d,%d" size="%d,25" font="Regular;20" halign="left" foregroundColor="#0038FF48" zPosition="2" noWrap="1" transparent="1" />
		</screen>
		""" % (w, h, w, h, s, s, w-(s*2), h-(s*2), s+5, s+2, s+25, s+2, s+45, s, w-(s*2)-50)

	def __init__(self, session, fileList, index, path, filename):
		Screen.__init__(self, session)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"], {
			"cancel": self.keyCancel,
			"left"  : self.keyLeft,
			"right" : self.keyRight,
			"blue"  : self.keyBlue,
			"yellow": self.keyYellow,
		}, -1)

		self["icon"]    = Pixmap()
		self["image"]   = Pixmap()
		self["status"]  = Pixmap()
		self["message"] = StaticText(_("Please wait, Loading image."))

		self.fileList     = []
		self.currentImage = []

		self.lsatIndex      = index
		self.startIndex     = index
		self.filename				= filename
		self.fileListLen    = 0
		self.currentIndex   = 0
		self.directoryCount = 0

		self.displayNow = True

		self.makeFileList(fileList, path)

		self.pictureLoad = ePicLoad()
		self.pictureLoad.PictureData.get().append(self.finishDecode)

		self.slideShowTimer = eTimer()
		self.slideShowTimer.callback.append(self.cbSlideShow)

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		if self.fileListLen >= 0:
			self.setPictureLoadPara()

	def keyLeft(self):
		self.currentImage = []
		self.currentIndex = self.lsatIndex
		self.currentIndex -= 1
		if self.currentIndex < 0:
			self.currentIndex = self.fileListLen
		self.startDecode()
		self.displayNow = True

	def keyRight(self):
		self.displayNow = True
		self.showPicture()

	def keyYellow(self):
		if self.fileListLen < 0:
			return
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Exif
		self.session.open(Pic_Exif, self.pictureLoad.getInfo(self.fileList[self.lsatIndex]))

	def keyBlue(self):
		if self.slideShowTimer.isActive():
			self.slideShowTimer.stop()
			self["icon"].hide()
		else:
			CONFIG_SLIDESHOW = config.plugins.filecommander.diashow.value
			self.slideShowTimer.start(CONFIG_SLIDESHOW)
			self["icon"].show()
			self.keyRight()

	def keyCancel(self):
		del self.pictureLoad
		self.close(self.startIndex)

	def setPictureLoadPara(self):
		sc = AVSwitch().getFramebufferScale()
		self.pictureLoad.setPara([self["image"].instance.size().width(), 
					  self["image"].instance.size().height(), 
					  sc[0],
					  sc[1],
					  0,
					  int(config.pic.resize.value),
					  '#00000000'])
		self["icon"].hide()
		if config.pic.infoline.value == False:
			self["message"].setText("")
		self.startDecode()

	def makeFileList(self, fileList, path):
		i = 0
		start_pic = -1
		for x in fileList:
			l = len(fileList[0])
			if x[0][0] is not None:
				testfilename = x[0][0].lower()
			else:
				testfilename = x[0][0] #"empty"
			if l == 3 or l == 2:
				if (x[0][1] == False) and ((testfilename.endswith(".jpg")) or (testfilename.endswith(".jpeg")) or (testfilename.endswith(".jpe")) or (testfilename.endswith(".png")) or (testfilename.endswith(".bmp"))):
					if self.filename == x[0][0]:
						start_pic = i
					i += 1
					self.fileList.append(path + x[0][0])
				else:	self.directoryCount += 1
			else:
				testfilename = x[4].lower()
				if (testfilename.endswith(".jpg")) or (testfilename.endswith(".jpeg")) or (testfilename.endswith(".jpe")) or (testfilename.endswith(".png")) or (testfilename.endswith(".bmp")):
					if self.filename == x[0][0]:
						start_pic = i
					i += 1
					self.fileList.append(x[4])
		self.currentIndex = start_pic
		if self.currentIndex < 0 or start_pic < 0:
			self.currentIndex = 0
		self.fileListLen = len(self.fileList) - 1


	def showPicture(self):
		if self.displayNow and len(self.currentImage):
			self.displayNow = False
			self["message"].setText(self.currentImage[0])
			self.lsatIndex = self.currentImage[1]
			self["image"].instance.setPixmap(self.currentImage[2].__deref__())
			self.currentImage = []

			self.currentIndex += 1

			if self.currentIndex > self.fileListLen:
				self.currentIndex = 0
			self.startDecode()

	def finishDecode(self, picInfo=""):
		self["status"].hide()
		ptr = self.pictureLoad.getData()
		if ptr != None:
			text = ""
			try:
				text = picInfo.split('\n',1)
				text = "(" + str(self.currentIndex+1) + "/" + str(self.fileListLen+1) + ") " + text[0].split('/')[-1]
			except:
				pass
			self.currentImage = []
			self.currentImage.append(text)
			self.currentImage.append(self.currentIndex)
			self.currentImage.append(ptr)
			self.showPicture()

	def startDecode(self):
		if len(self.fileList) == 0:
			self.currentIndex = 0
		self.pictureLoad.startDecode(self.fileList[self.currentIndex])
		self["status"].show()

	def cbSlideShow(self):
		print "slide to next Picture index=" + str(self.lsatIndex)
		if config.pic.loop.value==False and self.lsatIndex == self.fileListLen:
			self.PlayPause()
		self.displayNow = True
		self.showPicture()
