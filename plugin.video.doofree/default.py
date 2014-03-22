import re, urllib2, urllib
import json
import xbmcaddon, xbmcplugin, xbmcgui

ADDON = xbmcaddon.Addon(id='plugin.video.doofree')
PATH = 'doofree'
VERSION = '1.0.3'

base_url = ''
addon_handle = ''

master_json = "https://raw.githubusercontent.com/mpie/doofree/master/master.json"
seesantv = "http://www.seesantv.com/seesantv_2014/"
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

def getContent(url):
    content = urllib2.urlopen(url).read()
    return content

def parseJson(url):
    req = urllib2.Request(url, None)
    opener = urllib2.build_opener()
    f = opener.open(req)
    data = json.loads(f.read())
    return data

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def addDirItem(url, name, image):
    item = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=image)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=item, isFolder=True)
    
def addDir(name, url, mode, image):
    url = build_url({'mode': mode, 'name': name, 'url': url})
    ok = addDirItem(url, name, image)
    return ok

def addThaiDir(name, url, mode, image):
    url = build_url({'mode': mode, 'url': url})
    ok = addDirItem(url, name, image)
    return ok

def addThaiLink(name, url, mode, image):
    url = build_url({'mode': mode, 'name': name.encode('tis-620'), 'url': url})
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
    contextMenuItems = []
    item.addContextMenuItems(contextMenuItems, replaceItems=True)
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=item, isFolder=False)
    return ok

def HOME():
    data = parseJson(master_json)
    for item in data['Home']:
        addDir(item['title'].encode("utf-8"), item['location'], 1, '')
    xbmcplugin.endOfDirectory(addon_handle)

def INDEX(name, url):
    if url.endswith('.json'):
        ''
    else:
        link = getContent(url)
        link=''.join(link.splitlines()).replace('\'','"')
        limatch=re.compile('<figure>(.+?)</a><figcaption>').findall(link)
        for licontent in limatch:
            show=re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)">').findall(licontent)
            title = show[0][2].decode('tis-620')
            addThaiDir(title, seesantv + show[0][0] + '&page=0', 2, show[0][1])

def getEpisodes(url):
    link = getContent(url + '&vdo_type=.mp4')
    link = ''.join(link.splitlines()).replace('\'','"')
    link=''.join(link.splitlines()).replace('<i class="icon-new"></i>','')
    episodematch = re.compile('<table class="program-archive">(.+?)</table>').findall(link)
    #print episodematch
    episodes = re.compile('<a href="(.+?)" >(.+?)</a> </td>                           \t\t\t\t\t\t\t<td>\t\t\t\t\t\t\t\t<a href="(.+?)" ><img').findall(episodematch[0])
    #print episodes
    programMeta = re.compile('<div class="program-meta">(.+?)</div>').findall(link)
    image = re.compile('<img src="(.+?)" alt').findall(programMeta[0])[0]
    for episode in episodes:
        #print episode[1].decode('tis-620')
        addThaiLink(episode[1].decode('tis-620'), seesantv + episode[0], 3, image)
    # paginator
    paginator=re.compile('<div class="page_list"  align="center">(.+?)</ul>').findall(link)[0]
    #print paginator
    pages=re.compile('>(\d+)</a>').findall(paginator)
    if len(pages)>1:
        for page in pages:
            pag = int (page[0]) - 1
            pageUrl = url + '&vdo_type=.mp4&page=' + str (pag)
            addThaiDir('page ' + page[0], pageUrl, 2, image)
                
def getParams():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring)>= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?','')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params=getParams()
url=None
name=None
mode=None
serverurl=None
pageurl=None
playpath=None
try:
    url=urllib.unquote_plus(params['url'])
except:
    pass
try:
    name=urllib.unquote_plus(params['name'])
except:
    pass
try:
    mode=int(params['mode'])
except:
    pass
try:
    serverurl=urllib.unquote_plus(params['serverurl'])
except:
    pass
try:
    pageurl=urllib.unquote_plus(params['pageurl'])
except:
    pass
try:
    playpath=urllib.unquote_plus(params['playpath'])
except:
    pass

sysarg=str(sys.argv[1])
if mode==None or url==None or len(url)<1:
    #getEpisodes("http://www.seesantv.com/seesantv_2014/program_detail.php?id=5409")
    HOME()
elif mode==1:
    INDEX(name, url)
elif mode==2:
    getEpisodes(url)
elif mode==4:
    SEARCH(url)
elif mode==6:
    ChooseServerReg(url)
elif mode==7:
    getVideoUrl(url)
elif mode==8:
    GetLoginCookie(cj, cookiefile)
elif mode==9:
    GetServerList("/sorted_01_0111.txt",url)
elif mode==10:
    GetServerList("/sorted_01_0110.txt",url)
elif mode==11:
    GetServerList("/sorted_02_0112.txt",url)
elif mode==12:
    GetServerList("/sorted_01_0711.txt",url)
elif mode==13:
    showLiveTV()
elif mode==14:
    playVideo(serverurl, url)
elif mode==15:
    playTv(serverurl)

xbmcplugin.endOfDirectory(addon_handle)
