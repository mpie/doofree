# -*- coding: utf-8 -*-

import xbmc,xbmcplugin
from resources.lib.tools import control

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database


class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)

    def playLiveStream(self, name, url, image):
        item = control.item(path=url)
        item.setArt({'icon': image})
        item.setInfo(type='Video', infoLabels={'title': name})
        item.setProperty('Video', 'true')
        item.setProperty('IsPlayable', 'true')
        control.playlist.clear()

        control.player.play(url)
