# -*- coding: utf-8 -*-

import sys, xbmcaddon
from urllib.parse import parse_qsl

# update repo
addonInfo = xbmcaddon.Addon().getAddonInfo

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')

name = params.get('name')

title = params.get('title')

year = params.get('year')

imdb = params.get('imdb')

tvdb = params.get('tvdb')

season = params.get('season')

episode = params.get('episode')

tvshowtitle = params.get('tvshowtitle')

premiered = params.get('premiered')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

select = params.get('select')

query = params.get('query')

source = params.get('source')

try:
    skin = params.get('skin')
except:
    skin = 500

# More thai params
content = params.get('content')
catid = params.get('catid')
showid = params.get('showid')
limit = params.get('limit')
channel = params.get('channel')
# End thai params

page = params.get('page')
if page is None:
    page = 0

if action is None:
    from resources.lib.indexers import navigator
    navigator.root()

elif action == 'thaiLiveTV':
    from resources.lib.indexers import navigator
    navigator.thai_live_tv()

elif action == 'thaiShows':
    from resources.lib.indexers import navigator
    navigator.thai_shows()

elif action == 'playLiveTV':
    from resources.lib.tools import player
    player.player().playLiveStream(name, url, image)

elif action == 'playThaiLiveTV':
    from resources.lib.tools import player
    player.player().playLiveStream(name, url, image)

elif action == 'listShows':
    from resources.lib.indexers import thai
    thai.thai().list_shows(catid, page)

elif action == 'listEpisodes':
    from resources.lib.indexers import thai
    thai.thai().list_episodes(catid, showid, page, image)

elif action == 'sourcePage':
    from resources.lib.indexers import thai
    thai.thai().source_page(url, name, image)
