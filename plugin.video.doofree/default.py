import re, urllib2, urllib
import simplejson as json
import xbmcaddon, xbmcplugin, xbmcgui

ADDON = xbmcaddon.Addon(id='plugin.video.doofree')
PATH = 'doofree'
VERSION = '1.0.3'

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

def HOME():
    addDir('Live Tv', '/videos/categories', 13, '')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def addDir(name, url, mode, iconimage):
    url = build_url({'mode': 'folder', 'foldername': 'Folder One'})
    ok = True
    li = xbmcgui.ListItem('Folder One', iconImage='DefaultFolder.png')
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                     listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)
    return ok

HOME()

xbmcplugin.endOfDirectory(addon_handle)
