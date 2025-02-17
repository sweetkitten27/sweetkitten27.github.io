# -*- coding: utf-8 -*-
#
#      Copyright (C) 2014 Tommy Winther
#      http://tommy.winther.nu
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscren (2016)
#      by primaeval - primaeval.dev@gmail.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import xbmc, xbmcvfs
from xml.etree import ElementTree
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import os
import re
import xbmcaddon, urllib
from strings import*
try: translatePath = xbmcvfs.translatePath
except: translatePath = xbmc.translatePath

addon    = 'script.ivueguide'
addon2    = 'plugin.video.intervue'
ADDONID  = addon
PVRID  = 'pvr.iptvsimple'
datapath = translatePath(os.path.join('special://profile', 'addon_data', addon))
inipath  = translatePath(os.path.join('special://profile', 'addon_data', addon2, 'resources', 'ini'))

def read(filename):
    f = file(filename, 'r')
    content = f.read()
    f.close()
    return content
def readlines(filename):
    lines = read(filename)
    lines = lines.replace('\r', '')
    lines = lines.split('\n')
    return lines
def GetSetting(param):
    return xbmcaddon.Addon(ADDONID).getSetting(param)
def PvrSetting(param):
    return xbmcaddon.Addon(PVRID).getSetting(param)
def get(param, file):
    try:    config = readlines(file)
    except: return None
    for line in config:
        if line.startswith(param):
            return line.split(param, 1)[-1].split('=', 1)[-1].strip()
    return None
def walk(folder):
    list = xbmcvfs.listdir(folder)
    return folder, list[0], list[1] 

class StreamsService(object):
    def __init__(self, addon):
        self.addon = addon
        self.strings = channelstrings('Z3VpLnB5', 143415)
        path = translatePath(os.path.join('special://profile', 'addon_data', 'script.ivueguide', 'addons.ini'))
        xbmc.log('[script.ivueguide] addons.ini is used', xbmc.LOGDEBUG)

        try:self.addonsParser = ConfigParser(strict=False, dict_type=OrderedDict, interpolation=None)
        except:self.addonsParser = ConfigParser(dict_type=OrderedDict)
        self.addonsParser.optionxform = lambda option: option

        # Default append addons.ini only
        #try:
            #self.addonsParser.read(path, 'UTF-8')
        #except:
            #pass

        iniFiles = self.getIniFiles()

        #for file in iniFiles:
        self.addonsParser.read(iniFiles)
            #except: pass


    #custom append ini files
    def getIniFiles(self):
        files = []
        import glob
        ini   = os.path.join(inipath, '*.*')# import all from resources ini
        
        files = glob.glob(ini)

        # Append inis  
        files.append(os.path.join(datapath,'addons.ini'))
        files.append(os.path.join(datapath,'addons2.ini'))

			
        return files

    def loadFavourites(self):
        entries = list()
        path = translatePath(os.path.join('special://profile', 'favourites.xml'))
        if os.path.exists(path):
            f = open(path, 'rb')
            xml = f.read()
            f.close()             
 
            try:
                doc = ElementTree.fromstring(xml)
                for node in doc.findall('favourite'):
                    value = node.text
                    value = node.text.replace(',return','')
                    if value[0:11] == 'PlayMedia("':
                        value = value[11:-2]
                    elif value[0:10] == 'PlayMedia(':
                        value = value[10:-1]
                    elif value[0:22] == 'ActivateWindow(10025,"':
                        value = value[22:-2]
                    elif value[0:21] == 'ActivateWindow(10025,':
                        value = value[22:-1]
                    elif value[0:22] == 'ActivateWindow(10001,"':
                        value = value[22:-2]
                    elif value[0:21] == 'ActivateWindow(10001,':
                        value = value[22:-1]
                    else:
                        continue

                    entries.append((node.get('name'), value))
            except:
                pass

        return entries


    def loadSuperFavs(self):
        try:
            xbmcaddon.Addon('plugin.program.super.favourites')
        except Exception:
            return # ignore addons that are not installed
        entries = list()
        path = translatePath(os.path.join('special://profile', 'addon_data', 'plugin.program.super.favourites'))
        if os.path.exists(path):
            for root, dirs, files in os.walk(path): 
                for file in files:
                    if file == 'favourites.xml':
                         f = open(os.path.join(root, file), 'rb')
                         xml = f.read()
                         f.close()             
 
                         try:
                             doc = ElementTree.fromstring(xml)
                             for node in doc.findall('favourite'):
                                 value = node.text
                                 value = node.text.replace(',return','')
                                 if value[0:11] == 'PlayMedia("':
                                     value = value[11:-2]
                                 elif value[0:10] == 'PlayMedia(':
                                     value = value[10:-1]
                                 elif value[0:22] == 'ActivateWindow(10025,"':
                                     value = value[22:-2]
                                 elif value[0:21] == 'ActivateWindow(10025,':
                                     value = value[22:-1]
                                 elif value[0:22] == 'ActivateWindow(10001,"':
                                     value = value[22:-2]
                                 elif value[0:21] == 'ActivateWindow(10001,':
                                     value = value[22:-1]
                                 else:
                                     continue

                                 entries.append((node.get('name'), value))
                         except:
                             pass

        return entries
		
		

    def getAddons(self):
        return self.addonsParser.sections()

    def getAddonStreams(self, id):
        if id:
            return self.addonsParser.items(id)

    def detectReminder(self, channel):
 
        #kodiFaves = self.loadFavourites() kills fuzzy and favs do not use


        # check all addons and return all matches
        matches = []
        exact_matches = []
        sub_matches = []
        numword_matches = []
        if self.strings == None: stringConfig(1)
        for id in self.getAddons():
            try:
                xbmcaddon.Addon(id)
            except Exception:
                continue # ignore addons that are not installed

            for label, stream in self.getAddonStreams(id):

                if label.lower() == channel.lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                if int(self.addon.getSetting('addon.match')) > 0:
                    labelx = re.sub(r' ','',label.lower())
                    title = re.sub(r' ','',channel.lower().replace(':',''))
                    titleRe = r".*%s.*" % re.escape(title)
                    if re.match(titleRe,labelx):
                        sub_matches.append((id, label, stream))

        kodiFaves = self.loadFavourites()
        superFavs = self.loadSuperFavs()
        if kodiFaves:
            id = 'kodi-favourite'           
            for (label, stream) in kodiFaves:

                if label.lower() == str(channel.title).lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                if int(self.addon.getSetting('addon.match')) > 0:
                    labelx = re.sub(r' ','',label.lower())
                    title = re.sub(r' ','',str(channel.title).lower().replace(':',''))
                    titleRe = r".*%s.*" % re.escape(title)
                    if re.match(titleRe,labelx):
                        sub_matches.append((id, label, stream))

        if superFavs:
            id = 'super-favourite'           
            for (label, stream) in superFavs:
                if label.lower() == str(channel.title).lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                if int(self.addon.getSetting('addon.match')) > 0:
                    labelx = re.sub(r' ','',label.lower())
                    title = re.sub(r' ','',str(channel.title).lower().replace(':',''))
                    titleRe = r".*%s.*" % re.escape(title)
                    if re.match(titleRe,labelx):
                        sub_matches.append((id, label, stream))


        exact_matches = set(exact_matches)
        sorted_exact_matches = sorted(exact_matches, key=lambda match: match[1])
        sub_matches = set(sub_matches) - set(exact_matches)
        sorted_sub_matches = sorted(sub_matches, key=lambda match: match[1])
        matches = sorted_exact_matches
        if int(self.addon.getSetting('addon.match')) > 0:
            matches = matches + sorted_sub_matches

        if len(matches) == 1:

            if not self.addon.getSetting('ignore.stream'):
                return matches[0][2]
            else:
                return matches

        else:
            return matches


    def detectStream(self, channel):
        """
        @param channel:
        @type channel: source.Channel
        """
        #kodiFaves = self.loadFavourites() kills fuzzy and favs do not use


        # check all addons and return all matches
        matches = []
        exact_matches = []
        sub_matches = []
        numword_matches = []
        if self.strings == None: stringConfig(1)
        for id in self.getAddons():
            try:
                xbmcaddon.Addon(id)
            except Exception:
                continue # ignore addons that are not installed

            for label, stream in self.getAddonStreams(id):
                if type(stream) is list:
                    stream = stream[0]
                if id == "plugin.video.meta":
                    label = channel.title
                    stream = str(stream.replace("<channel>", channel.title.replace(" ","%20")))


                if label.lower() == str(channel.title).lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                if int(self.addon.getSetting('addon.match')) > 0:
                    labelx = re.sub(r' ','',label.lower())
                    title = re.sub(r' ','',str(channel.title).lower().replace(':',''))
                    titleRe = r".*%s.*" % re.escape(title)
                    if re.match(titleRe,labelx):
                        sub_matches.append((id, label, stream))

        kodiFaves = self.loadFavourites()
        superFavs = self.loadSuperFavs()
        if kodiFaves:
            id = 'kodi-favourite'           
            for (label, stream) in kodiFaves:

                if label.lower() == str(channel.title).lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                if int(self.addon.getSetting('addon.match')) > 0:
                    labelx = re.sub(r' ','',label.lower())
                    title = re.sub(r' ','',str(channel.title).lower().replace(':',''))
                    titleRe = r".*%s.*" % re.escape(title)
                    if re.match(titleRe,labelx):
                        sub_matches.append((id, label, stream))


        if superFavs:
            id = 'super-favourite'           
            for (label, stream) in superFavs:
                if label.lower() == str(channel.title).lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                if int(self.addon.getSetting('addon.match')) > 0:
                    labelx = re.sub(r' ','',label.lower())
                    title = re.sub(r' ','',str(channel.title).lower().replace(':',''))
                    titleRe = r".*%s.*" % re.escape(title)
                    if re.match(titleRe,labelx):
                        sub_matches.append((id, label, stream))

        exact_matches = set(exact_matches)
        sorted_exact_matches = sorted(exact_matches, key=lambda match: match[1])
        sub_matches = set(sub_matches) - set(exact_matches)
        sorted_sub_matches = sorted(sub_matches, key=lambda match: match[1])
        matches = sorted_exact_matches
        if int(self.addon.getSetting('addon.match')) > 0:
            matches = matches + sorted_sub_matches


        if len(matches) == 1:

            if not self.addon.getSetting('ignore.stream'):
                return matches[0][2]
            else:
                return matches

        else:
            return matches


    def detectStreams(self, channel):
        matches = []
        exact_matches = []
        sub_matches = []
        numword_matches = []
        if self.strings == None: stringConfig(1)
        for id in self.getAddons():
            try:
                xbmcaddon.Addon(id)
            except Exception:
                continue # ignore addons that are not installed

            for (label, stream) in self.getAddonStreams(id):
                if type(stream) is list:
                    stream = stream[0]
                if id == "plugin.video.meta":
                    label = channel
                    stream = str(stream.replace("<channel>", channel.replace(" ","%20")))


                if label.lower() == channel.lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                labelx = re.sub(r' ','',label.lower())
                title = re.sub(r' ','',channel.lower().replace(':',''))
                labelRe = r".*%s.*" % re.escape(labelx)
                titleRe = r".*%s.*" % re.escape(title)
                if re.match(titleRe,labelx):
                    sub_matches.append((id, label, stream))
                elif re.match(labelRe,title) and label != 'e':
                    sub_matches.append((id, label, stream))

        kodiFaves = self.loadFavourites()
        superFavs = self.loadSuperFavs()
        if kodiFaves:
            id = 'kodi-favourite'           
            for (label, stream) in kodiFaves:

                if label.lower() == channel.lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                labelx = re.sub(r' ','',label.lower())
                title = re.sub(r' ','',channel.lower().replace(':',''))
                labelRe = r".*%s.*" % re.escape(labelx)
                titleRe = r".*%s.*" % re.escape(title)
                if re.match(titleRe,labelx):
                    sub_matches.append((id, label, stream))
                elif re.match(labelRe,title) and label != 'e':
                    sub_matches.append((id, label, stream))

        if superFavs:
            id = 'super-favourite'           
            for (label, stream) in superFavs:
                if label.lower() == channel.lower().replace(':',''):
                    exact_matches.append((id, label, stream))
                labelx = re.sub(r' ','',label.lower())
                title = re.sub(r' ','',channel.lower().replace(':',''))
                labelRe = r".*%s.*" % re.escape(labelx)
                titleRe = r".*%s.*" % re.escape(title)
                if re.match(titleRe,labelx):
                    sub_matches.append((id, label, stream))
                elif re.match(labelRe,title) and label != 'e':
                    sub_matches.append((id, label, stream))



        exact_matches = set(exact_matches)
        sorted_exact_matches = sorted(exact_matches, key=lambda match: match[1])
        sub_matches = set(sub_matches) - set(exact_matches)
        sorted_sub_matches = sorted(sub_matches, key=lambda match: match[1])
        matches = sorted_exact_matches
        matches = matches + sorted_sub_matches

        return matches

class OrderedDict(dict):
    # From: http://code.activestate.com/recipes/576693/
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as for regular dictionaries.

    # The internal self.__map dictionary maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # Each link is stored as a list of length three:  [PREV, NEXT, KEY].


    def __init__(self, *args, **kwds):
        '''Initialize an ordered dictionary.  Signature is the same as for
        regular dictionaries, but keyword arguments are not recommended
        because their insertion order is arbitrary.

        '''
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__root
        except AttributeError:
            self.__root = root = []                     # sentinel node
            root[:] = [root, root, None]
            self.__map = {}
        self.__update(*args, **kwds)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link which goes at the end of the linked
        # list, and the inherited dictionary is updated with the new key/value pair.
        if key not in self:
            root = self.__root
            last = root[0]
            last[1] = root[0] = self.__map[key] = [last, root, key]
        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> del od[y]'
        # Deleting an existing item uses self.__map to find the link which is
        # then removed by updating the links in the predecessor and successor nodes.
        dict_delitem(self, key)
        link_prev, link_next, key = self.__map.pop(key)
        link_prev[1] = link_next
        link_next[0] = link_prev

    def __iter__(self):
        'od.__iter__() <==> iter(od)'
        root = self.__root
        curr = root[1]
        while curr is not root:
            yield curr[2]
            curr = curr[1]

    def __reversed__(self):
        'od.__reversed__() <==> reversed(od)'
        root = self.__root
        curr = root[0]
        while curr is not root:
            yield curr[2]
            curr = curr[0]

    def clear(self):
        'od.clear() -> None.  Remove all items from od.'
        try:
            for node in self.__map.itervalues():
                del node[:]
            root = self.__root
            root[:] = [root, root, None]
            self.__map.clear()
        except AttributeError:
            pass
        dict.clear(self)

    def popitem(self, last=True):
        '''od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order if false.

        '''
        if not self:
            raise KeyError('dictionary is empty')
        root = self.__root
        if last:
            link = root[0]
            link_prev = link[0]
            link_prev[1] = root
            root[0] = link_prev
        else:
            link = root[1]
            link_next = link[1]
            root[1] = link_next
            link_next[0] = root
        key = link[2]
        del self.__map[key]
        value = dict.pop(self, key)
        return key, value

    # -- the following methods do not depend on the internal structure --

    def keys(self):
        'od.keys() -> list of keys in od'
        return list(self)

    def values(self):
        'od.values() -> list of values in od'
        return [self[key] for key in self]

    def items(self):
        'od.items() -> list of (key, value) pairs in od'
        return [(key, self[key]) for key in self]

    def iterkeys(self):
        'od.iterkeys() -> an iterator over the keys in od'
        return iter(self)

    def itervalues(self):
        'od.itervalues -> an iterator over the values in od'
        for k in self:
            yield self[k]

    def iteritems(self):
        'od.iteritems -> an iterator over the (key, value) items in od'
        for k in self:
            yield (k, self[k])

    def update(*args, **kwds):
        '''od.update(E, **F) -> None.  Update od from dict/iterable E and F.

        If E is a dict instance, does:           for k in E: od[k] = E[k]
        If E has a .keys() method, does:         for k in E.keys(): od[k] = E[k]
        Or if E is an iterable of items, does:   for k, v in E: od[k] = v
        In either case, this is followed by:     for k, v in F.items(): od[k] = v


        '''
        if len(args) > 2:
            raise TypeError('update() takes at most 2 positional '
                            'arguments (%d given)' % (len(args),))
        elif not args:
            raise TypeError('update() takes at least 1 argument (0 given)')
        self = args[0]
        # Make progressively weaker assumptions about "other"
        other = ()
        if len(args) == 2:
            other = args[1]
        if isinstance(other, dict):
            for key in other:
                self[key] = other[key]
        elif hasattr(other, 'keys'):
            for key in other.keys():
                self[key] = other[key]
        else:
            for key, value in other:
                self[key] = value
        for key, value in kwds.items():
            self[key] = value

    __update = update  # let subclasses override update without breaking __init__

    __marker = object()

    def pop(self, key, default=__marker):
        '''od.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.

        '''
        if key in self:
            result = self[key]
            del self[key]
            return result
        if default is self.__marker:
            raise KeyError(key)
        return default

    def setdefault(self, key, default=None):
        'od.setdefault(k[,d]) -> od.get(k,d), also set od[k]=d if k not in od'
        if key in self:
            return self[key]
        self[key] = default
        return default

    def __repr__(self, _repr_running={}):
        'od.__repr__() <==> repr(od)'
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.items())
        finally:
            del _repr_running[call_key]

    def __reduce__(self):
        'Return state information for pickling'
        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        for k in vars(OrderedDict()):
            inst_dict.pop(k, None)
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def copy(self):
        'od.copy() -> a shallow copy of od'
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S
        and values equal to v (which defaults to None).

        '''
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
        while comparison to a regular mapping is order-insensitive.

        '''
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other