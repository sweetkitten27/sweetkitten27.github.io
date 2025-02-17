# -*- coding: utf-8 -*-
#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com

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
import datetime
import os
import xbmc
import xbmcgui
import source as src

from strings import *

ADDONID = 'script.ivueguide'
ADDON = xbmcaddon.Addon(ADDONID)
HOME = ADDON.getAddonInfo('path')


class Notification(object):
    def __init__(self, database, addonPath):
        """
        @param database: source.Database
        """
        self.database = database
        self.addonPath = addonPath
        self.icon = os.path.join(self.addonPath, 'icon.png')

    def createAlarmClockName(self, programTitle, startTime):
        return 'tvguide-%s-%s' % (programTitle, startTime)

    def scheduleNotifications(self):
        xbmc.log("[script.ivueguide] Scheduling notifications")
        for channelId, channelTitle, programTitle, startTime in self.database.getNotifications():
            self._scheduleNotification(channelId, channelTitle, programTitle, startTime)

    def _scheduleNotification(self, channelId, channelTitle, programTitle, startTime):
        t = startTime - datetime.datetime.now()
        timeToNotification = ((t.days * 86400) + t.seconds) / 60
        if timeToNotification < 0:
            return

        name = self.createAlarmClockName(programTitle, startTime)

        description = strings(NOTIFICATION_5_MINS, channelTitle)
        xbmc.executebuiltin('AlarmClock(%s-5mins,Notification(%s,%s,10000,%s),%d,True)' %
            (name, programTitle, description, self.icon, timeToNotification - 5))

        path = os.path.join(HOME, 'playPlanner.py')
        description = strings(NOTIFICATION_NOW, channelTitle)

        value  =       programTitle 
        value += ',' + str(channelTitle)
        value += ',' + str(channelId)
        value += ',' + description

        xbmc.executebuiltin('AlarmClock(%s-now,RunScript(%s,%s),%d,True)' %
                            (name, path, value, timeToNotification))

    def _unscheduleNotification(self, programTitle, startTime):
        name = self.createAlarmClockName(programTitle, startTime)
        xbmc.executebuiltin('CancelAlarm(%s-5mins,True)' % name)
        xbmc.executebuiltin('CancelAlarm(%s-now,True)' % name)

    def addNotification(self, program):
        self.database.addNotification(program)
        self._scheduleNotification(program.channel.id, program.channel.title, program.title, program.startDate)

    def removeNotification(self, program):
        self.database.removeNotification(program)
        self._unscheduleNotification(program.title, program.startDate)


if __name__ == '__main__':
    database = src.Database()

    def onNotificationsCleared():
        xbmcgui.Dialog().ok(strings(CLEAR_NOTIFICATIONS), strings(DONE))

    def onInitialized(success):
        if success:
            database.clearAllNotifications()
            database.close(onNotificationsCleared)
        else:
            database.close()

    database.initialize(onInitialized)
