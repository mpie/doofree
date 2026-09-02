# -*- coding: utf-8 -*-

import sys, re, json, urllib
from urllib.parse import parse_qsl, urlparse

try:
    action = dict(parse_qsl(sys.argv[2].replace('?', '')))['action']
except:
    action = None

from resources.lib.tools import bookmarks, client, control, player, views

addonFanart = control.addonFanart()
sysaddon = sys.argv[0]


def _int(value, default=1):
    """Parse a page number that may arrive as None, '' or junk."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _quote(value):
    """Escape a value so it survives being put in a plugin:// query string."""
    return urllib.parse.quote_plus(value if value is not None else '')


class thai:
    def __init__(self):
        self.list = []
        self.img1 = 'https://seesantv.com/'
        self.img2 = 'https://www.seesantv.com/seesantv2020/file_management/images/programs'
        self.main_link = 'https://seesantv.com/seesantv2020/%s'
        self.login_link = self.main_link % 'apps/index.php?module=members&task=checkLogin'
        self.shows_link = self.main_link % 'apps/index.php?module=programs&task=setLoadListTypeAll&category=%s&page=%s'
        self.episodes_link = self.main_link % 'apps/index.php?module=programs&task=setLoadChapterListByPages2020&program_id=%s&page=%s'
        self.player_link = self.main_link % 'player-%s'
        self.geo_link = 'http://ip-api.com/json/'
        self.member_id = 217280
        self.view_server_id = 403  # 405 = gm, 403 = uk
        self.replace_server = 'gm99'  # uk1, uk2, gm1, gm2, us1, us3, us4, as1, as2, jp1, jp2
        self.User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'

    def get_cookies(self, geo_check=False):
        parts = ['ssCheckLogin2=1']

        # Viewers inside Thailand are served by a different streaming server.
        if geo_check:
            parts.append('viewServersID=%d' % self.view_server())

        parts.append('ssMemberID=%d' % self.member_id)
        parts.append('ssMemberUsername=%s' % 'endy.adorian%40niickel.us')
        parts.append('ssMemberPassword=%s' % 'test12345')
        return '; '.join(parts)

    def view_server(self):
        """Streaming server id to request, based on where the viewer is."""
        try:
            result = client.request(self.geo_link, headers=self.get_headers(self.geo_link))
            data = json.loads(result)
            if data.get('countryCode') == 'TH':
                return 409
        except Exception:
            pass
        return self.view_server_id

    def get_headers(self, ref_url, url=None):
        """Headers for a request to `url` (defaults to `ref_url`).

        The Host header has to match the host actually being addressed; sending
        seesantv's Host to another service breaks that request.
        """
        target = url or ref_url
        host = urlparse(target).netloc or urlparse(self.main_link % '').netloc
        return {'Host': host, 'Referer': ref_url, 'User-Agent': self.User_Agent}

    '''
    List all the shows from a specific category
    '''

    def list_shows(self, catid, page):
        syshandle = int(sys.argv[1])
        page = _int(page, 1)
        url = self.shows_link % (catid, page)

        try:
            result = client.request(url, headers=self.get_headers(url), cookie=self.get_cookies())
            data = json.loads(result)
            pageContent = data['content']
        except Exception:
            control.infoDialog('Could not load this category', icon='ERROR')
            control.directory(syshandle, succeeded=False)
            return

        limatch = re.compile('<figure>(.+?)</a></li>').findall(pageContent)

        for li_content in limatch:
            # One unparsable tile must not take the whole category down.
            show = re.compile('program-(.+?)" target.+?src="(.+?)".+?h5>(.+?)</h5').findall(li_content)
            if not show:
                continue
            showid, image, title = show[0][0], show[0][1], show[0][2]

            if 'program_pic/program_' in image:
                image = image.replace('../', self.img1)
            else:
                image = image.replace('../', self.img2)
                image = image.replace('program_pic', '')

            self.list.append({'name': title, 'showid': showid, 'image': image})

        if not self.list:
            control.infoDialog('No shows on this page')
            control.directory(syshandle, succeeded=False)
            return

        for show in self.list:
            name = show['name']
            showid = show['showid']
            image = show['image']
            query = '?action=listEpisodes&name=%s&catid=%s&showid=%s&image=%s&page=1' % (
                _quote(name), _quote(catid), _quote(showid), _quote(image))
            url = '%s%s' % (sysaddon, query)
            item = control.item(name)
            item.setArt({'icon': image})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
            item.setInfo(type="Video", infoLabels={"Title": name, "OriginalTitle": name})
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)

        # The API does not report a page count, so paging is offered as long as
        # a page returns shows; the next page reports for itself when it is empty.
        self.add_page_item('Next page', '?action=listShows&catid=%s&page=%d' % (_quote(catid), page + 1))
        if page > 1:
            self.add_page_item('Previous page', '?action=listShows&catid=%s&page=%d' % (_quote(catid), page - 1))

        control.content(syshandle, 'tvshows')
        control.directory(syshandle, cacheToDisc=True)
        views.set_view('tvshows', {'skin.estuary': 500, 'skin.confluence': 500})

    def add_page_item(self, name, query):
        """Add a paging entry to the current directory."""
        item = control.item(name)
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        item.setInfo(type="Video", infoLabels={"Title": name, "OriginalTitle": name})
        control.addItem(handle=int(sys.argv[1]), url='%s%s' % (sysaddon, query), listitem=item, isFolder=True)

    '''
    List all shows episodes
    Page starts at 0
    '''

    def list_episodes(self, catid, showid, page, image):
        syshandle = int(sys.argv[1])
        page = _int(page, 1)
        url = self.episodes_link % (showid, page)

        try:
            result = client.request(url, headers=self.get_headers(url), cookie=self.get_cookies())
            data = json.loads(result)
            r = client.parseDOM(data['list'], 'li')
        except Exception:
            control.infoDialog('Could not load the episode list', icon='ERROR')
            control.directory(syshandle, succeeded=False)
            return

        for li in r:
            # Skip entries that do not carry both a link and a title.
            try:
                href = client.parseDOM(li, 'a', ret='href')[0]
                anchor = client.parseDOM(li, 'a')[0]
                name = re.compile('<i class="fas fa-play-circle-player "></i> (.+)').findall(anchor)[0]
            except IndexError:
                continue
            self.list.append({'name': name, 'page_url': href, 'url': _quote(href), 'image': image})

        if not self.list:
            control.infoDialog('No episodes on this page')
            control.directory(syshandle, succeeded=False)
            return

        for episode in self.list:
            name = episode['name']
            page_url = episode['page_url']
            query = '?action=sourcePage&image=%s&url=%s&name=%s' % (
                _quote(episode['image']), episode['url'], _quote(name))
            url = '%s%s' % (sysaddon, query)

            # A part-watched episode shows how far you got and can be reset from
            # the context menu.
            position, duration = bookmarks.get(page_url)
            label = name
            context_items = []
            if position >= bookmarks.MIN_RESUME_SECONDS:
                label = '%s [COLOR gold](%s)[/COLOR]' % (name, bookmarks.time_label(position))
                context_items.append((
                    'DooFree: clear resume point',
                    'RunPlugin(%s?action=clearResume&url=%s)' % (sysaddon, episode['url']),
                ))

            item = control.item(label)
            item.setArt({'icon': episode['image']})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
            item.setInfo(type="Video", infoLabels={"Title": name, "OriginalTitle": name})
            if position:
                # Read by skins to draw the partly-watched progress bar.
                item.setProperty('ResumeTime', str(position))
                item.setProperty('TotalTime', str(duration if duration else position + 1))
            if context_items:
                item.addContextMenuItems(context_items)
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)

        # Same as the show list: page on while pages keep returning episodes, and
        # carry the artwork along so paged listings keep their poster.
        base = '?action=listEpisodes&catid=%s&showid=%s&image=%s' % (
            _quote(catid), _quote(showid), _quote(image))
        self.add_page_item('Next page', '%s&page=%d' % (base, page + 1))
        if page > 1:
            self.add_page_item('Previous page', '%s&page=%d' % (base, page - 1))

        control.content(syshandle, 'episodes')
        control.directory(syshandle, cacheToDisc=True)
        views.set_view('episodes', {'skin.estuary': 55, 'skin.confluence': 50})

    '''
    Get the video url by member_id cookie
    Start playing the video
    '''

    def source_page(self, url, name, image):
        try:
            result = client.request(url, cookie=self.get_cookies(geo_check=True),
                                    headers=self.get_headers(url))
            vidFile = re.compile('file: "(.+?)"').findall(result.decode('utf-8'))[0]
        except IndexError:
            # No `file:` in the page: the session is refused or the page changed.
            control.infoDialog('No playable stream found for this episode', icon='ERROR')
            return
        except Exception:
            control.infoDialog('Could not reach the source page', icon='ERROR')
            return

        videoUrl = self.full_quality(vidFile)

        # The resume point is stored under the page URL: the resolved video URL
        # carries a session token and differs on every play.
        player.player().playStream(name, videoUrl + '|Referer:' + url, image, resume_url=url)

    def full_quality(self, video_url):
        """Swap the downscaled `...s.mp4` file for the full-size one.

        Anchored on the extension, so a title that merely ends in an "s" - say
        `specials.mp4` - is left alone.
        """
        return re.sub(r's\.mp4(?=$|\?)', '.mp4', video_url)
