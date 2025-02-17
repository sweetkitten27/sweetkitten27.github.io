#
#       Copyright (C) 2014-
#       Sean Poyser (seanpoyser@gmail.com)
#       Portions Copyright (c) 2021 John Moore
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
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import sys, os, time
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import favourite
import utils


ADDON   = utils.ADDON
ADDONID = utils.ADDONID
FRODO   = utils.FRODO


PLAYMEDIA_MODE      = utils.PLAYMEDIA_MODE
ACTIVATEWINDOW_MODE = utils.ACTIVATEWINDOW_MODE
RUNPLUGIN_MODE      = utils.RUNPLUGIN_MODE
ACTION_MODE         = utils.ACTION_MODE
SHOWPICTURE_MODE    = utils.SHOWPICTURE_MODE

PLAY_PLAYLISTS = ADDON.getSetting('PLAY_PLAYLISTS') == 'true'
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU    =   10



def getParentCommand(cmd):
    parents = []

    import re
    try:
        plugin = re.compile('plugin://(.+?)/').search(cmd.replace('?', '/')).group(1)

        md5 = utils.generateMD5(plugin)
        
        if md5 not in parents:
            return None

        if xbmc.getCondVisibility('System.HasAddon(%s)' % plugin) == 1:
            return 'plugin://%s' % plugin

    except Exception as e:
        pass 
  
    return None


def processParentCommand(cmd):
    parent = getParentCommand(cmd)

    if not parent:
        return

    xbmc.executebuiltin('Container.Update(%s)' % parent)
    while not xbmc.getInfoLabel('Container.FolderPath').startswith(parent):
        xbmc.sleep(50)
    


def playCommand(originalCmd, contentMode=False):
    try:
        xbmc.executebuiltin('Dialog.Close(busydialog)') #Isengard fix
 
        cmd = favourite.tidy(originalCmd)

        if cmd.lower().startswith('executebuiltin'):
            cmd = cmd.replace('"', '')
            cmd = cmd.lower()
            cmd = cmd.replace('"', '')
            cmd = cmd.replace('executebuiltin(', '')
            if cmd.endswith('))'):
                cmd = cmd[:-1]
            if cmd.endswith(')') and '(' not  in cmd:
                cmd = cmd[:-1]
     
        #if a 'Super Favourite' favourite just do it
        #if ADDONID in cmd:
        #     return xbmc.executebuiltin(cmd)

        #if in contentMode just do it
        if contentMode:
            xbmc.executebuiltin('ActivateWindow(Home)') #some items don't play nicely if launched from wrong window
            if cmd.lower().startswith('activatewindow'):
                cmd = cmd.replace('")', '",return)') #just in case return is missing    
            return xbmc.executebuiltin(cmd)

        if cmd.startswith('RunScript'):    
            #workaround bug in Frodo that can cause lock-up
            #when running a script favourite
            if FRODO:
                xbmc.executebuiltin('ActivateWindow(Home)')

        if PLAY_PLAYLISTS:
            import playlist
            if playlist.isPlaylist(cmd):
                return playlist.play(cmd)      

        if 'ActivateWindow' in cmd:
            return activateWindowCommand(cmd)

        if 'PlayMedia' in cmd:
            return playMedia(originalCmd)

        xbmc.executebuiltin(cmd)


    except Exception as e:
        utils.log('Error in playCommand')
        utils.log('Command: %s' % cmd)
        utils.log('Error:   %s' % str(e))    


def activateWindowCommand(cmd):
    utils.log("***activateWindowCommand called")
    property = 'SF_BROWSER_PATH'
    cmds = cmd.split(',', 1)

    #special case for filemanager
    if '10003' in cmds[0] or 'filemanager' in cmds[0].lower():
        xbmc.executebuiltin(cmd)
        return

    plugin      = None
    activate    = None
    pluginArgs  = None

    if len(cmds) == 1:
        activate = cmds[0]
    else:
        activate = cmds[0]+',return)'
        if "plugin://"in cmds[1][:-1]:
            plugin   = cmds[1][:-1]
            try:
                pluginArgs = plugin.split('/?',1)[1]
            except: pass

    #check if it is a different window and if so activate it
    id = str(xbmcgui.getCurrentWindowId())

    if id not in activate:
        xbmc.executebuiltin(activate)

    if plugin and not pluginArgs is None:
        utils.log("Plugin With Args Called...")
        try:
            if "2Fcategories" in cmd:
                utils.log("2F: xbmc.executebuiltin(cmd)")
                xbmc.executebuiltin(cmd)
            elif 'mode=' in plugin.lower():
                utils.log("mode: xbmc.executebuiltin(cmd)")
                xbmc.executebuiltin(cmd)
            elif 'action=' in plugin.lower():
                utils.log("action: xbmc.executebuiltin(cmd)")
                xbmc.executebuiltin(cmd)
            else:
                if 'type%3avideo' in pluginArgs:
                    utils.log("video: xbmc.executebuiltin('RunPlugin(%s)' % plugin)")
                    xbmc.executebuiltin('RunPlugin(%s)' % plugin)
                elif 'type%3arss' in pluginArgs:
                    utils.log("rss: xbmc.executebuiltin(cmd)")
                    xbmc.executebuiltin(cmd)
                else:
                    utils.log("refdir: xbmc.executebuiltin(cmd)")
                    xbmc.executebuiltin(cmd)
        except Exception as e:
            utils.log(str(e))

        xbmcgui.Window(10000).clearProperty(property)
    else:
        folderpath = xbmc.getInfoLabel('Container.FolderPath')
        utils.log(f"***folder path: {folderpath}")
        prop = xbmcgui.Window(10000).getProperty(property)

        if plugin:
            utils.log("Plugin Without Args Called...")
            path = plugin.split(',', 1)[0]

            if not prop:
                xbmcgui.Window(10000).setProperty(property, folderpath)
                xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
                xbmc.executebuiltin('Container.Update(%s)' % path)
            else:
                xbmcgui.Window(10000).clearProperty(property)
                xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
                xbmc.executebuiltin("Action(Back, 10025)")
        else:  # Folder or Directory Resource
            path = os.path.normpath(cmd.split(',', 2)[1])
            utils.log("Directory Resource Called...")

            if not prop:
                xbmcgui.Window(10000).setProperty(property, path)
                xbmc.executebuiltin(f"Container.Update({path})")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
            else:
                xbmcgui.Window(10000).clearProperty(property)
                xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
                xbmc.executebuiltin("Action(Back, 10025)")




def playMedia(original):
    import re
    cmd = favourite.tidy(original) #.replace(',', '') #remove spurious commas
    processParentCommand(cmd)

    try:    mode = int(favourite.getOption(original, 'mode'))
    except: mode = 0

    if mode == PLAYMEDIA_MODE:  
        xbmc.executebuiltin(cmd)
        return

    plugin = re.compile('"(.+?)"').search(cmd).group(1)

    if mode == SHOWPICTURE_MODE:  
        xbmc.executebuiltin('ShowPicture(%s)' % plugin)
        return

    if len(plugin) < 1:
        xbmc.executebuiltin(cmd)
        return

    if mode == ACTIVATEWINDOW_MODE:   
        try:    winID = int(favourite.getOption(original, 'winID'))
        except: winID = 10025

        #check if it is a different window and if so activate it
        id = xbmcgui.getCurrentWindowId()

        if id != winID :
            xbmc.executebuiltin('ActivateWindow(%d)' % winID)
            
        cmd = 'Container.Update(%s)' % plugin

        xbmc.executebuiltin(cmd)
        return

    if mode == RUNPLUGIN_MODE:
        cmd = 'RunPlugin(%s)' % plugin

        xbmc.executebuiltin(cmd)
        return

    #if all else fails just execute it
    xbmc.executebuiltin(cmd)

   