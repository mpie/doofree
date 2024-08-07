# -*- coding: utf-8 -*-

import os, sys, xbmcaddon

from resources.lib.tools import control, views

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
control.moderator()
artPath = control.artPath()
addonFanart = control.addonFanart()
queueMenu = 'Queue'

def root():
    add_directory_item('Live TV', 'thaiLiveTV', 'root_thaitv.png', 'DefaultMovies.png')
    add_directory_item('Shows', 'thaiShows', 'root_thaishows.png', 'DefaultMovies.png')
    end_directory()
    views.set_view('movies', {'skin.estuary': 500, 'skin.confluence': 500})


def end_directory():
    control.content(syshandle, 'addons')
    control.directory(syshandle, cacheToDisc=True)


def add_directory_item(name, query, thumb, icon, context=None, queue=False, is_action=True, is_folder=True):
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

    item = control.item(label=name)
    item.addContextMenuItems(cm)
    item.setArt({'icon': thumb, 'thumb': thumb})

    if addonFanart is not None:
        item.setProperty('Fanart_Image', addonFanart)

    control.addItem(handle=syshandle, url=url, listitem=item, isFolder=is_folder)

def thai_live_tv():
    add_directory_item('ONE',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/chone-3/playlist.m3u8'
                       '&name=ONE_HD'
                       '&image=ch1hd.png',
                       'ch1hd.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('3HD',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/ch3hd-3/playlist.m3u8'
                       '&name=3HD'
                       '&image=ch3hd.png',
                       'ch3hd.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('PPTV',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/chpptv-3/playlist.m3u8'
                       '&name=PPTV'
                       '&image=ch3sd.png',
                       'ch3sd.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('GMM',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/chgmmchannel-3/playlist.m3u8'
                       '&name=3Family'
                       '&image=ch3family.png',
                       'ch3family.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('5HD',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/ch5hd-1/playlist.m3u8'
                       '&name=5HD'
                       '&image=ch5hd.png',
                       'ch5hd.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('7HD',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/ch7hd-3/playlist.m3u8'
                       '&name=7HD'
                       '&image=ch7hd.png',
                       'ch7hd.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('8HD',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/cheight-3/playlist.m3u8'
                       '&name=8HD'
                       '&image=ch8hd.png',
                       'ch8hd.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('Workpoint',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/chworkpointt-3/playlist.m3u8'
                       '&name=WORKPOINT'
                       '&image=chworkpoint.png',
                       'chworkpoint.png', 'DefaultMovies.png', is_folder=False)
    add_directory_item('TNN',
                       'playThaiLiveTV'
                       '&url=https://live-gm.thaimomo.com/live-as/chtnn24-2/playlist.m3u8'
                       '&name=TNN'
                       '&image=DefaultMovies.png',
                       'DefaultMovies.png', 'DefaultMovies.png', is_folder=False)
    end_directory()


def thai_shows():
    add_directory_item('ละครไทย (ออนแอร์) / Thai Dramas (on air)', 'listShows&catid=18&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ละครไทย (อวสาน) / Thai Dramas (ended)', 'listShows&catid=27&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ซีรี่ย์เกาหลี / Korean Series', 'listShows&catid=17&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('หนังจีนชุด / Chinese Series', 'listShows&catid=37&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('รายการอาหาร / Cooking Shows', 'listShows&catid=15&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('วาไรตี้โชว์ / Variety Shows', 'listShows&catid=8&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('เรียลลิตี้โชว์ / Reality & Singing Contest', 'listShows&catid=84&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('เกมส์โชว์ / Game Shows', 'listShows&catid=2&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ข่าว / Thai News', 'listShows&catid=4&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ทอล์กโชว์ / Talk Shows', 'listShows&catid=3&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ภาพยนตร์ไทย / Thai Movies', 'listShows&catid=92&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ภาพยนตร์ฝรั่งใหม่ / US Movies (Thai dubbed)', 'listShows&catid=98&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ซีรี่ย์ฝรั่ง / US Series (Thai dubbed)', 'listShows&catid=38&page=1', '',
                       'DefaultMovies.png')
    add_directory_item('ภาพยนตร์แอนนิเมชั่น / Animation', 'listShows&catid=93&page=1', '',
                       'DefaultMovies.png')
    end_directory()
