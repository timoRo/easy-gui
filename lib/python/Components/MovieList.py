import os
import struct
import random

from enigma import eListboxPythonMultiContent, eListbox, gFont, iServiceInformation, eSize, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, eServiceReference, eServiceCenter, eTimer

from GUIComponent import GUIComponent
from Tools.FuzzyDate import FuzzyTime
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryProgress
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import SCOPE_ACTIVE_SKIN, resolveFilename
from Screens.LocationBox import defaultInhibitDirs
import NavigationInstance
import skin


AUDIO_EXTENSIONS = frozenset((".dts", ".mp3", ".wav", ".wave", ".ogg", ".flac", ".m4a", ".mp2", ".m2a", ".3gp", ".3g2", ".asf", ".wma"))
DVD_EXTENSIONS = ('.iso', '.img')
IMAGE_EXTENSIONS = frozenset((".jpg", ".jpeg", ".png", ".gif", ".bmp"))
MOVIE_EXTENSIONS = frozenset((".mpg", ".mpeg", ".vob", ".wav", ".m4v", ".mkv", ".avi", ".divx", ".dat", ".flv", ".mp4", ".mov", ".wmv", ".m2ts"))
KNOWN_EXTENSIONS = MOVIE_EXTENSIONS.union(IMAGE_EXTENSIONS, DVD_EXTENSIONS, AUDIO_EXTENSIONS)

cutsParser = struct.Struct('>QI') # big-endian, 64-bit PTS and 32-bit type

class MovieListData:
	def __init__(self):
		pass

# iStaticServiceInformation
class StubInfo:
	def __init__(self):
		pass

	def getName(self, serviceref):
		if serviceref.getPath().endswith('/'):
			return serviceref.getPath()
		else:
			return os.path.basename(serviceref.getPath())
	def getLength(self, serviceref):
		return -1
	def getEvent(self, serviceref, *args):
		return None
	def isPlayable(self):
		return True
	def getInfo(self, serviceref, w):
		try:
			if w == iServiceInformation.sTimeCreate:
				return os.stat(serviceref.getPath()).st_ctime
			if w == iServiceInformation.sFileSize:
				return os.stat(serviceref.getPath()).st_size
			if w == iServiceInformation.sDescription:
				return serviceref.getPath()
		except:
			pass
		return 0
	def getInfoString(self, serviceref, w):
		return ''
justStubInfo = StubInfo()

def lastPlayPosFromCache(ref):
	from Screens.InfoBarGenerics import resumePointCache
	return resumePointCache.get(ref.toString(), None)

def moviePlayState(cutsFileName, ref, length):
	"""Returns None, 0..100 for percentage"""
	try:
		# read the cuts file first
		f = open(cutsFileName, 'rb')
		lastCut = None
		cutPTS = None
		while 1:
			data = f.read(cutsParser.size)
			if len(data) < cutsParser.size:
				break
			cut, cutType = cutsParser.unpack(data)
			if cutType == 3: # undocumented, but 3 appears to be the stop
				cutPTS = cut
			else:
				lastCut = cut
		f.close()
		# See what we have in RAM (it might help)
		last = lastPlayPosFromCache(ref)
		if last:
			# Get the length from the cache
			if not lastCut:
				lastCut = last[2]
			# Get the cut point from the cache if not in the file
			if not cutPTS:
				cutPTS = last[1]
		if cutPTS is None:
			# Unseen movie
			return None
		if not lastCut:
			if length and (length > 0):
				lastCut = length * 90000
			else:
				# dunno
				return 0
		if cutPTS >= lastCut:
			return 100
		return (100 * cutPTS) // lastCut
	except:
		cutPTS = lastPlayPosFromCache(ref)
		if cutPTS:
			if not length or (length<0):
				length = cutPTS[2]
			if length:
				if cutPTS[1] >= length:
					return 100
				return (100 * cutPTS[1]) // length
			else:
				return 0
		return None

def resetMoviePlayState(cutsFileName, ref=None):
	try:
		if ref is not None:
			from Screens.InfoBarGenerics import delResumePoint
			delResumePoint(ref)
		f = open(cutsFileName, 'rb')
		cutlist = []
		while 1:
			data = f.read(cutsParser.size)
			if len(data) < cutsParser.size:
				break
			cut, cutType = cutsParser.unpack(data)
			if cutType != 3:
				cutlist.append(data)
		f.close()
		f = open(cutsFileName, 'wb')
		f.write(''.join(cutlist))
		f.close()
	except:
		pass
		#import sys
		#print "[MovieList] Exception in resetMoviePlayState: %s: %s" % sys.exc_info()[:2]

class MovieList(GUIComponent):
	SORT_ALPHANUMERIC = 1
	SORT_RECORDED = 2
	SHUFFLE = 3
	SORT_ALPHANUMERIC_REVERSE = 4
	SORT_RECORDED_REVERSE = 5
	SORT_ALPHANUMERIC_FLAT = 6
	SORT_ALPHANUMERIC_FLAT_REVERSE = 7

	HIDE_DESCRIPTION = 1
	SHOW_DESCRIPTION = 2

	dirNameExclusions = ['.AppleDouble', '.AppleDesktop', '.AppleDB',
				'Network Trash Folder', 'Temporary Items',
				'.TemporaryItems']

	def __init__(self, root, sort_type=None, descr_state=None):
		GUIComponent.__init__(self)
		self.list = []
		self.descr_state = descr_state or self.HIDE_DESCRIPTION
		self.sort_type = sort_type or self.SORT_RECORDED
		self.firstFileEntry = 0
		self.parentDirectory = 0
		self.fontName = "Regular"
		self.fontSize = 20
		self.listHeight = None
		self.listWidth = None
		self.reloadDelayTimer = None
		self.l = eListboxPythonMultiContent()
		self.tags = set()
		self.root = None
		self.list = None
		self._playInBackground = None
		self._playInForeground = None
		self._char = ''

		if root is not None:
			self.reload(root)

		self.l.setBuildFunc(self.buildMovieListEntry)

		self.onSelectionChanged = [ ]
		self.iconPart = []
		for part in range(5):
			self.iconPart.append(LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/part_%d_4.png" % part)))
		self.iconMovieRec = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/part_new.png"))
		self.iconMoviePlay = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/movie_play.png"))
		self.iconMoviePlayRec = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/movie_play_rec.png"))
		self.iconUnwatched = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/part_unwatched.png"))
		self.iconFolder = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/folder.png"))
		self.iconTrash = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/trashcan.png"))
		self.runningTimers = {}
		self.updateRecordings()
		self.updatePlayPosCache()

	def applySkin(self, desktop, screen):
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "font":
					font = skin.parseFont(value, ((1,1),(1,1)))
					self.fontName = font.family
					self.fontSize = font.pointSize
				else:
					attribs.append((attrib,value))
			self.skinAttributes = attribs
		rc = GUIComponent.applySkin(self, desktop, screen)
		self.listHeight = self.instance.size().height()
		self.listWidth = self.instance.size().width()
		self.setItemsPerPage()
		return rc

	def get_playInBackground(self):
		return self._playInBackground

	def set_playInBackground(self, value):
		if self._playInBackground is not value:
			index = self.findService(self._playInBackground)
			if index is not None:
				self.invalidateItem(index)
				self.l.invalidateEntry(index)
			index = self.findService(value)
			if index is not None:
				self.invalidateItem(index)
				self.l.invalidateEntry(index)
			self._playInBackground = value

	playInBackground = property(get_playInBackground, set_playInBackground)

	def get_playInForeground(self):
		return self._playInForeground

	def set_playInForeground(self, value):
		self._playInForeground = value

	playInForeground = property(get_playInForeground, set_playInForeground)

	def updatePlayPosCache(self):
		from Screens.InfoBarGenerics import updateresumePointCache
		updateresumePointCache()

	def updateRecordings(self, timer=None):
		if timer is not None:
			if timer.justplay:
				return
		result = {}
		for timer in NavigationInstance.instance.RecordTimer.timer_list:
			if timer.isRunning() and not timer.justplay:
				result[os.path.basename(timer.Filename)+'.ts'] = timer
		if self.runningTimers == result:
			return
		self.runningTimers = result
		if timer is not None:
			if self.reloadDelayTimer is not None:
				self.reloadDelayTimer.stop()
			self.reloadDelayTimer = eTimer()
			self.reloadDelayTimer.callback.append(self.reload)
			self.reloadDelayTimer.start(5000, 1)

	def connectSelChanged(self, fnc):
		if not fnc in self.onSelectionChanged:
			self.onSelectionChanged.append(fnc)

	def disconnectSelChanged(self, fnc):
		if fnc in self.onSelectionChanged:
			self.onSelectionChanged.remove(fnc)

	def selectionChanged(self):
		for x in self.onSelectionChanged:
			x()

	def setDescriptionState(self, val):
		self.descr_state = val

	def setSortType(self, type):
		self.sort_type = type

	def setItemsPerPage(self):
		if self.listHeight > 0:
			itemHeight = self.listHeight / config.movielist.itemsperpage.value
		else:
			itemHeight = 25 # some default (270/5)
		self.itemHeight = itemHeight
		self.l.setItemHeight(itemHeight)
		self.instance.resize(eSize(self.listWidth, self.listHeight / itemHeight * itemHeight))

	def setFontsize(self):
		self.l.setFont(0, gFont(self.fontName, self.fontSize + config.movielist.fontsize.value))
		self.l.setFont(1, gFont(self.fontName, (self.fontSize - 3) + config.movielist.fontsize.value))

	def invalidateItem(self, index):
		x = self.list[index]
		self.list[index] = (x[0], x[1], x[2], None)

	def invalidateCurrentItem(self):
		self.invalidateItem(self.getCurrentIndex())

	def buildMovieListEntry(self, serviceref, info, begin, data):
		switch = config.usage.show_icons_in_movielist.value
		width = self.l.getItemSize().width()
		pathName = serviceref.getPath()
		res = [None]

		if serviceref.flags & eServiceReference.mustDescent:
			# Directory
			iconSize = 22
			# Name is full path name
			if info is None:
				# Special case: "parent"
				txt = ".."
			else:
				txt = os.path.basename(os.path.normpath(pathName))
				if txt == ".Trash":
					res.append(MultiContentEntryPixmapAlphaTest(pos=(0, (self.itemHeight - 24) / 2), size=(iconSize, 24), flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, png=self.iconTrash))
					res.append(MultiContentEntryText(pos=(iconSize + 2, 0), size=(width - 166, self.itemHeight), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
					res.append(MultiContentEntryText(pos=(width - 145, 0), size=(145, self.itemHeight), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=_("Trashcan")))
					return res
			res.append(MultiContentEntryPixmapAlphaTest(pos=(0, (self.itemHeight - 24) / 2), size=(iconSize, iconSize), flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, png=self.iconFolder))
			res.append(MultiContentEntryText(pos=(iconSize + 2, 0), size=(width - 166, self.itemHeight), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
			res.append(MultiContentEntryText(pos=(width - 145, 0), size=(145, self.itemHeight), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=_("Directory")))
			return res
		if (data == -1) or (data is None):
			data = MovieListData()
			cur_idx = self.l.getCurrentSelectionIndex()
			x = self.list[cur_idx]  # x = ref,info,begin,...
			data.len = 0  # dont recalc movielist to speedup loading the list
			self.list[cur_idx] = (x[0], x[1], x[2], data)  # update entry in list... so next time we don't need to recalc
			data.txt = info.getName(serviceref)
			if config.movielist.hide_extensions.value:
				fileName, fileExtension = os.path.splitext(data.txt)
				if fileExtension in KNOWN_EXTENSIONS:
					data.txt = fileName
			data.icon = None
			data.part = None
			if os.path.basename(pathName) in self.runningTimers:
				if switch == 'i':
					if (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
						data.icon = self.iconMoviePlayRec
					else:
						data.icon = self.iconMovieRec
				elif switch == 'p' or switch == 's':
					data.part = 100
					if (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
						data.partcol = 0xffc71d
					else:
						data.partcol = 0xff001d
			elif (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
				data.icon = self.iconMoviePlay
			else:
				data.part = moviePlayState(pathName + '.cuts', serviceref, data.len)
				if data.part is not None and data.part <= 3:
					data.part = 0
				if data.part is not None and data.part >= 97:
					data.part = 100
				if switch == 'i':
					if data.part is not None and data.part > 0:
						data.icon = self.iconPart[data.part // 25]
					else:
						if config.usage.movielist_unseen.value:
							data.icon = self.iconUnwatched
				elif switch == 'p' or switch == 's':
					if data.part is not None and data.part > 0:
						data.partcol = 0xffc71d
					else:
						if config.usage.movielist_unseen.value:
							data.part = 100
							data.partcol = 0x206333
		len = data.len
		if len > 0:
			len = "%d:%02d" % (len / 60, len % 60)
		else:
			len = ""

		iconSize = 0
		if switch == 'i':
			iconSize = 22
			res.append(MultiContentEntryPixmapAlphaTest(pos=(0, (self.itemHeight - 20) / 2), size=(iconSize, 20), flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, png=data.icon))
		elif switch == 'p':
			iconSize = 48
			if data.part is not None and data.part > 0:
				res.append(MultiContentEntryProgress(pos=(0, (self.itemHeight - 16) / 2), size=(iconSize - 2, 16), percent=data.part, borderWidth=2, foreColor=data.partcol, foreColorSelected=None, backColor=None, backColorSelected=None))
			else:
				res.append(MultiContentEntryPixmapAlphaTest(pos=(0, (self.itemHeight - 20) / 2), size=(iconSize, 20), png=data.icon))
		elif switch == 's':
			iconSize = 22
			if data.part is not None and data.part > 0:
				res.append(MultiContentEntryProgress(pos=(0, (self.itemHeight - 16) / 2), size=(iconSize - 2, 16), percent=data.part, borderWidth=2, foreColor=data.partcol, foreColorSelected=None, backColor=None, backColorSelected=None))
			else:
				res.append(MultiContentEntryPixmapAlphaTest(pos=(0, (self.itemHeight - 20) / 2), size=(iconSize, 20), png=data.icon))

		begin_string = ""
		if begin > 0:
			begin_string = ' '.join(FuzzyTime(begin, inPast=True))

		ih = self.itemHeight
		lenSize = ih * 3  # 25 -> 75
		dateSize = ih * 145 / 25   # 25 -> 145
		res.append(MultiContentEntryText(pos=(iconSize, 0), size=(width - iconSize - dateSize, ih), flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, font=0, text=data.txt))
		res.append(MultiContentEntryText(pos=(width - dateSize, 0), size=(dateSize, ih), flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, font=1, text=begin_string))
		return res

	def moveToFirstMovie(self):
		if self.firstFileEntry < len(self.list):
			self.instance.moveSelectionTo(self.firstFileEntry)
		else:
			# there are no movies, just directories...
			self.moveToFirst()

	def moveToParentDirectory(self):
		if self.parentDirectory < len(self.list):
			self.instance.moveSelectionTo(self.parentDirectory)
		else:
			self.moveToFirst()

	def moveToLast(self):
		if self.list:
			self.instance.moveSelectionTo(len(self.list) - 1)

	def moveToFirst(self):
		if self.list:
			self.instance.moveSelectionTo(0)

	def moveToIndex(self, index):
		self.instance.moveSelectionTo(index)

	def getCurrentIndex(self):
		return self.instance.getCurrentIndex()

	def getCurrentEvent(self):
		l = self.l.getCurrentSelection()
		return l and l[0] and l[1] and l[1].getEvent(l[0])

	def getCurrent(self):
		l = self.l.getCurrentSelection()
		return l and l[0]

	def getItem(self, index):
		if self.list:
			if len(self.list) > index:
				return self.list[index] and self.list[index][0]

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		instance.setContent(self.l)
		instance.selectionChanged.get().append(self.selectionChanged)
		self.setFontsize()

	def preWidgetRemove(self, instance):
		instance.setContent(None)
		instance.selectionChanged.get().remove(self.selectionChanged)

	def reload(self, root = None, filter_tags = None):
		if self.reloadDelayTimer is not None:
			self.reloadDelayTimer.stop()
			self.reloadDelayTimer = None
		if root is not None:
			self.load(root, filter_tags)
		else:
			self.load(self.root, filter_tags)
		self.l.setList(self.list)

	def removeService(self, service):
		index = self.findService(service)
		if index is not None:
			del self.list[index]
			self.l.setList(self.list)

	def findService(self, service):
		if service is None:
			return None
		for index, l in enumerate(self.list):
			if l[0] == service:
				return index
		return None

	def __len__(self):
		return len(self.list)

	def __getitem__(self, index):
		return self.list[index]

	def __iter__(self):
		return self.list.__iter__()

	def load(self, root, filter_tags):
		# this lists our root service, then building a
		# nice list
		self.list = [ ]
		serviceHandler = eServiceCenter.getInstance()
		numberOfDirs = 0

		reflist = serviceHandler.list(root)
		if reflist is None:
			print "[MovieList] listing of movies failed"
			return
		realtags = set()
		tags = {}
		rootPath = os.path.normpath(root.getPath())
		parent = None
		# Don't navigate above the "root"
		if len(rootPath) > 1 and (os.path.realpath(rootPath) != config.movielist.root.value):
			parent = os.path.dirname(rootPath)
			# enigma wants an extra '/' appended
			if not parent.endswith('/'):
				parent += '/'
			ref = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + parent)
			ref.flags = eServiceReference.flagDirectory
			self.list.append((ref, None, 0, -1))
			numberOfDirs += 1
		while 1:
			serviceref = reflist.getNext()
			if not serviceref.valid():
				break
			info = serviceHandler.info(serviceref)
			if info is None:
				info = justStubInfo
			begin = info.getInfo(serviceref, iServiceInformation.sTimeCreate)
			if serviceref.flags & eServiceReference.mustDescent:
				dirname = info.getName(serviceref)
				normdirname = os.path.normpath(dirname)
				normname = os.path.basename(normdirname)
				if normname not in MovieList.dirNameExclusions and normdirname not in defaultInhibitDirs:
					self.list.append((serviceref, info, begin, -1))
					numberOfDirs += 1
				continue
			# convert space-seperated list of tags into a set
			this_tags = info.getInfoString(serviceref, iServiceInformation.sTags).split(' ')
			name = info.getName(serviceref)

			# OSX put a lot of stupid files ._* everywhere... we need to skip them
			if name[:2] == "._":
				continue

			if this_tags == ['']:
				# No tags? Auto tag!
				this_tags = name.replace(',',' ').replace('.',' ').replace('_',' ').replace(':',' ').split()
			else:
				realtags.update(this_tags)
			for tag in this_tags:
				if len(tag) >= 4:
					if tags.has_key(tag):
						tags[tag].append(name)
					else:
						tags[tag] = [name]
			# filter_tags is either None (which means no filter at all), or
			# a set. In this case, all elements of filter_tags must be present,
			# otherwise the entry will be dropped.
			if filter_tags is not None:
				this_tags_fullname = [" ".join(this_tags)]
				this_tags_fullname = set(this_tags_fullname)
				this_tags = set(this_tags)
				if not this_tags.issuperset(filter_tags) and not this_tags_fullname.issuperset(filter_tags):
# 					print "[MovieList] Skipping", name, "tags=", this_tags, " filter=", filter_tags
					continue

			self.list.append((serviceref, info, begin, -1))

		self.firstFileEntry = numberOfDirs
		self.parentDirectory = 0

		if self.sort_type == MovieList.SORT_ALPHANUMERIC:
			self.list.sort(key=self.buildAlphaNumericSortKey)
		elif self.sort_type == MovieList.SORT_ALPHANUMERIC_REVERSE:
			self.list.sort(key=self.buildAlphaNumericSortKey, reverse=True)
		elif self.sort_type == MovieList.SORT_ALPHANUMERIC_FLAT:
			self.list.sort(key=self.buildAlphaNumericFlatSortKey)
		elif self.sort_type == MovieList.SORT_ALPHANUMERIC_FLAT_REVERSE:
			self.list.sort(key=self.buildAlphaNumericFlatSortKey, reverse=True)
		elif self.sort_type == MovieList.SORT_RECORDED:
			self.list.sort(key=self.buildBeginTimeSortKey)
		elif self.sort_type == MovieList.SORT_RECORDED_REVERSE:
			self.list.sort(key=self.buildBeginTimeSortKey, reverse=True)
		elif self.sort_type == MovieList.SHUFFLE:
			self.list.sort(key=self.buildBeginTimeSortKey)
			dirlist = self.list[:numberOfDirs]
			shufflelist = self.list[numberOfDirs:]
			random.shuffle(shufflelist)
			self.list = dirlist + shufflelist

		for x in self.list[:]:
			if x[1]:
				tmppath = x[1].getName(x[0])[:-1] if x[1].getName(x[0]).endswith('/') else x[1].getName(x[0])
				if tmppath.endswith('.Trash'):
					self.list.append(self.list.pop(self.list.index(x)))
			else:
					self.list.insert(0, self.list.pop(self.list.index(x)))

		if self.root and numberOfDirs > 0:
			rootPath = os.path.normpath(self.root.getPath())
			if not rootPath.endswith('/'):
				rootPath += '/'
			if rootPath != parent:
				# with new sort types directories may be in between files, so scan whole
				# list for parentDirectory index. Usually it is the first one anyway
				for index, item in enumerate(self.list):
					if item[0].flags & eServiceReference.mustDescent:
						itempath = os.path.normpath(item[0].getPath())
						if not itempath.endswith('/'):
							itempath += '/'
						if itempath == rootPath:
							self.parentDirectory = index
							break
		self.root = root
		# finally, store a list of all tags which were found. these can be presented
		# to the user to filter the list
		# ML: Only use the tags that occur more than once in the list OR that were
		# really in the tag set of some file.

		# reverse the dictionary to see which unique movie each tag now references
		rtags = {}
		for tag, movies in tags.items():
			if (len(movies) > 1) or (tag in realtags):
				movies = tuple(movies) # a tuple can be hashed, but a list not
				item = rtags.get(movies, [])
				if not item: rtags[movies] = item
				item.append(tag)
		self.tags = {}
		for movies, tags in rtags.items():
			movie = movies[0]
			# format the tag lists so that they are in 'original' order
			tags.sort(key = movie.find)
			first = movie.find(tags[0])
			last = movie.find(tags[-1]) + len(tags[-1])
			match = movie
			start = 0
			end = len(movie)
			# Check if the set has a complete sentence in common, and how far
			for m in movies[1:]:
				if m[start:end] != match:
					if not m.startswith(movie[:last]):
						start = first
					if not m.endswith(movie[first:]):
						end = last
					match = movie[start:end]
					if m[start:end] != match:
						match = ''
						break
			if match:
				self.tags[match] = set(tags)
				continue
			else:
				match = ' '.join(tags)
				if len(match) > 2: #Omit small words
					self.tags[match] = set(tags)

	def buildAlphaNumericSortKey(self, x):
		# x = ref,info,begin,...
		ref = x[0]
		name = x[1] and x[1].getName(ref)
		if ref.flags & eServiceReference.mustDescent:
			return 0, name and name.lower() or "", -x[2]
		return 1, name and name.lower() or "", -x[2]

	def buildAlphaNumericFlatSortKey(self, x):
		# x = ref,info,begin,...
		ref = x[0]
		name = x[1] and x[1].getName(ref) or ".."
		if name and ref.flags & eServiceReference.mustDescent:
			# only use directory basename for sorting
			try:
				name = os.path.basename(os.path.normpath(name))
			except:
				pass
		if name.endswith(".Trash"):
			name = "Deleted Items"
		# print "[MovieList] Sorting for -%s-" % name

		return 1, name and name.lower() or "", -x[2]

	def buildBeginTimeSortKey(self, x):
		ref = x[0]
		if ref.flags & eServiceReference.mustDescent:
			try:
				mtime = -os.stat(ref.getPath()).st_mtime
			except:
				mtime = 0
			return 0, x[1] and mtime
		return 1, -x[2]

	def moveTo(self, serviceref):
		index = self.findService(serviceref)
		if index is not None:
			self.instance.moveSelectionTo(index)
			return True
		return False

	def moveDown(self):
		self.instance.moveSelection(self.instance.moveDown)

	def moveUp(self):
		self.instance.moveSelection(self.instance.moveUp)

	def moveToChar(self, char, lbl=None):
		self._char = char
		self._lbl = lbl
		if lbl:
			lbl.setText(self._char)
			lbl.visible = True
		self.moveToCharTimer = eTimer()
		self.moveToCharTimer.callback.append(self._moveToChrStr)
		self.moveToCharTimer.start(1000, True) #time to wait for next key press to decide which letter to use...

	def moveToString(self, char, lbl=None):
		self._char = self._char + char.upper()
		self._lbl = lbl
		if lbl:
			lbl.setText(self._char)
			lbl.visible = True
		self.moveToCharTimer = eTimer()
		self.moveToCharTimer.callback.append(self._moveToChrStr)
		self.moveToCharTimer.start(1000, True) #time to wait for next key press to decide which letter to use...

	def _moveToChrStr(self):
		currentIndex = self.instance.getCurrentIndex()
		index = currentIndex + 1
		if index >= len(self.list):
			index = 0
		while index != currentIndex:
			item = self.list[index]
			if item[1] is not None:
				ref = item[0]
				itemName = getShortName(item[1].getName(ref), ref)
				strlen = len(self._char)
				if strlen == 1 and itemName.startswith(self._char) \
				or strlen > 1 and itemName.find(self._char) >= 0:
					self.instance.moveSelectionTo(index)
					break
			index += 1
			if index >= len(self.list):
				index = 0
		self._char = ''
		if self._lbl:
			self._lbl.visible = False

def getShortName(name, serviceref):
	if serviceref.flags & eServiceReference.mustDescent: #Directory
		pathName = serviceref.getPath()
		name = os.path.basename(os.path.normpath(pathName))
		if name == '.Trash':
			name = _("Deleted items")
	return name.upper()
