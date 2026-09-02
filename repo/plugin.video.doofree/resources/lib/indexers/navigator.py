# -*- coding: utf-8 -*-

import os, sys, xbmcaddon
from urllib.parse import quote_plus

from resources.lib.tools import control, remote_config, views

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
control.moderator()
artPath = control.artPath()
addonFanart = control.addonFanart()
queueMenu = 'Queue'

def root():
    add_directory_item('Live TV', 'thaiLiveTV', 'root_thaitv.png', 'DefaultMovies.png')
    add_directory_item('Shows', 'thaiShows', 'root_thaishows.png', 'DefaultMovies.png',
                       context_items=[('DooFree: clear all resume points',
                                       'RunPlugin(%s?action=clearAllResume)' % sysaddon)])
    end_directory()
    views.set_view('movies', {'skin.estuary': 500, 'skin.confluence': 500})


def end_directory():
    control.content(syshandle, 'addons')
    control.directory(syshandle, cacheToDisc=True)


def add_directory_item(name, query, thumb, icon, context=None, queue=False, is_action=True, is_folder=True,
                       context_items=None):
    try:
        name = control.lang(name).encode('utf-8')
    except:
        pass
    url = '%s?action=%s' % (sysaddon, query) if is_action else query
    thumb = os.path.join(artPath, thumb) if not artPath == None else icon
    cm = []
    if queue:
        cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

    if context is not None:
        cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))

    # Ready-made (label, built-in command) pairs, no string-id lookup involved.
    if context_items:
        cm.extend(context_items)

    item = control.item(label=name)
    item.addContextMenuItems(cm)
    item.setArt({'icon': thumb, 'thumb': thumb})

    if addonFanart is not None:
        item.setProperty('Fanart_Image', addonFanart)

    control.addItem(handle=syshandle, url=url, listitem=item, isFolder=is_folder)

def thai_live_tv():
    """Live channels, as listed by the configuration file."""
    channels = remote_config.live_channels()
    if not channels:
        control.infoDialog('No channels available right now', icon='ERROR')
        control.directory(syshandle, succeeded=False)
        return

    for channel in channels:
        image = channel.get('image') or 'DefaultMovies.png'
        query = 'playThaiLiveTV&url=%s&name=%s&image=%s' % (
            quote_plus(channel['url']),
            quote_plus(channel.get('title') or channel['name']),
            quote_plus(image))
        add_directory_item(channel['name'], query, image, 'DefaultMovies.png', is_folder=False)

    end_directory()


def thai_shows():
    """Show categories, as listed by the configuration file."""
    categories = remote_config.categories()
    if not categories:
        control.infoDialog('No categories available right now', icon='ERROR')
        control.directory(syshandle, succeeded=False)
        return

    for category in categories:
        query = 'listShows&catid=%s&page=1' % quote_plus(str(category['catid']))
        add_directory_item(category['name'], query, '', 'DefaultMovies.png')

    end_directory()
