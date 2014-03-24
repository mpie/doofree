import re, urllib2, urllib, json
import random

master_json = "https://raw.githubusercontent.com/mpie/doofree/master/json/master.json"
seesantv = "http://www.seesantv.com/seesantv_2014/"

"""
{u'Home': [{u'location': u'https://raw.githubusercontent.com/mpie/doofree/master/json/new_movies.json', u'id': 1, u'title': u'New Movies'}, {u'location': u'https://raw.githubusercontent.com/mpie/doofree/master/json/new_series.json', u'id': 2, u'title': u'New Series'}]}
"""
class Crawler:
    crawlCounter = 0
    series = [4, 5]
    locationParentId = 0
    
    def __init__(self, master_url):
        self.master_url = master_url + '?' + str(random.random())
        self.trySD = True
        self.hostNumber = 0

    def crawl(self):
        data = self.parseJson(self.master_url)
        for item in data['Home']:
            if 'page' in item:
                print "Crawling %s" % item['title'].encode("utf-8"), "Url: %s" % item['page']
                content = self.getContent(item['page'])
                records = self.findMovies(content, item['id'])
                jsonString = self.createJson(records)
                if len(jsonString) > 0:
                    location = 'json/categories/' + str(item['id']) + '.json'
                    print "Write content to: %s" % location
                    self.writeFile(location, jsonString)
                    self.createList()
        
    def getContent(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        Crawler.crawlCounter += 1
        response.close()
        return html

    def parseJson(self, url):
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        data = json.loads(f.read())
        return data

    def createJson(self, records):
        return json.dumps(records, sort_keys=True, indent=4)

    def writeFile(self, location, string):
        f = open(location, 'w')
        f.write(string)
        f.close()

    def findMovies(self, content, parent_id):
        self.movies = []
        movies = re.compile('<figure>(.+?)</a><figcaption>').findall(content)
        for movie in movies:
            show = re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)">').findall(movie)
            title = show[0][2].decode('tis-620')
            product_id = re.compile('id=(\d+)').findall(show[0][0])[0]
            location = "https://raw.githubusercontent.com/mpie/doofree/master/json/products/" + product_id + ".json"
            record = {'parent_id': parent_id, 'id': int (product_id), 'title':title, 'location': location, 'page':seesantv + show[0][0], 'thumbnail':show[0][1]}
            self.movies.append(record)
        fullContent = {'isFolder': True, 'list': self.movies}
        return fullContent

    def createList(self):
        if Crawler.crawlCounter == 1:
            for item in self.movies:
                product_id = re.compile('id=(\d+)').findall(item['page'])[0]
                if item['parent_id'] in Crawler.series:
                    page = 0
                    url = self.composeUrl(item['page'], page) 
                    content = self.getContent(url)
                    parent_id = item['id']
                    records = self.findEpisodes(parent_id, content)
                    jsonString = self.createJson(records)
                    if len(jsonString) > 0:
                        location = 'json/products/' + product_id + '.json'
                        print "Write episodes to: %s" % location
                        self.writeFile(location, jsonString)

    def findEpisodes(self, parent_id, content):
        self.episodes = []
        content = ''.join(content.splitlines()).replace('<i class="icon-new"></i>','')
        episodematch = re.compile('<table class="program-archive">(.+?)</table>').findall(content)
        episodes = re.compile('<a href="(.+?)" >(.+?)</a> </td>                           \t\t\t\t\t\t\t<td>\t\t\t\t\t\t\t\t<a href="(.+?)" ><img').findall(episodematch[0])

        programMeta = re.compile('<div class="program-meta">(.+?)</div>').findall(content)
        image = re.compile('<img src="(.+?)" alt').findall(programMeta[0])[0]

        topInfo = re.compile('<div class="top-info">(.+?)</div>').findall(content)
        channel = re.compile('<img src="(.+?)" width').findall(topInfo[0])
        if (len(channel) > 0):
            channel = 'ch' + channel[0][-5]
            if (channel == 'chv'):
                channel = 'chthaipbs'
        else:
            channel = 'chall'

        for episode in episodes:
            title = episode[1].decode('tis-620')
            url = episode[0]
            location = self.getLocation(parent_id, title, url, channel)
            if 'video has been removed' != location:
                record = {'title':title, 'location':location, 'thumbnail':image}
                self.episodes.append(record)
        fullContent = {'isFolder': False, 'list': self.episodes}
        return fullContent
    
    def composeUrl(self, url, page):
        return url + '&vdo_type=.mp4&page=' + str(page)

    def getLocation(self, parent_id, title, url, channel):        
        trySD = True
        program_id = re.compile('program_id=(\d+)').findall(url)[0]
        if (len(program_id) < 5):
            program_id = '0' + program_id
        fullDate = re.compile('(\d+-\d+-\d+) ').findall(title)[0]
        date = ''.join(fullDate.splitlines()).replace('-','')
        hd = channel + '/' + program_id + '/' + date + '1-' + program_id + '.mp4'
        sd = channel + '/' + program_id + '/' + date + '-' + program_id + '.mp4'

        if parent_id == Crawler.locationParentId:
            if False == self.trySD:
                return "http://uk" + str (self.hostNumber) + ".seesantv.com/" + hd
            else:
                return "http://uk" + str (self.hostNumber) + ".seesantv.com/" + sd
            
        for host in range(1, 31):
            fullurl = "http://uk" + str (host) + ".seesantv.com/" + hd
            found = self.exists(fullurl)
            if (found):
                self.hostNumber = host
                self.trySD = False
                Crawler.locationParentId = parent_id
                return fullurl
        if (trySD):
            for host in range(1, 31):
                fullurl = "http://uk" + str (host) + ".seesantv.com/" + sd
                found = self.exists(fullurl)
                if (found):
                    self.hostNumber = host
                    self.trySD = True
                    Crawler.locationParentId = parent_id
                    return fullurl
        return 'video has been removed'
            
    def exists(self, url):
        try:
            r = urllib2.urlopen(url, timeout=1)
            if r.getcode() == 200:
                return True
        except urllib2.URLError, e:
            return False

crawler = Crawler(master_json)
crawler.crawl()
'''
    for item in data['Home']:
        if 'page' in item:
            items = crawl(item['page'])
            if len(items)>0:
                print json.dumps(items)
                break

def crawl(url):
    items = [{'isFolder': True, 'list':[]}]
    link = getContent(url)
    link=''.join(link.splitlines()).replace('\'','"')
    limatch=re.compile('<figure>(.+?)</a><figcaption>').findall(link)
    for licontent in limatch:
        show=re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)">').findall(licontent)
        title = show[0][2].decode('tis-620')
        record = {'title':title, 'page':seesantv + show[0][0], 'thumbnail':show[0][1]}
        items.append(record)
    return items
    # paginator
    #createPagination(url)

init()

def getEpisodes(url):
    link = getContent(url + '&vdo_type=.mp4')
    link = ''.join(link.splitlines()).replace('\'','"')
    link=''.join(link.splitlines()).replace('<i class="icon-new"></i>','')

    episodematch = re.compile('<table class="program-archive">(.+?)</table>').findall(link)
    episodes = re.compile('<a href="(.+?)" >(.+?)</a> </td>                           \t\t\t\t\t\t\t<td>\t\t\t\t\t\t\t\t<a href="(.+?)" ><img').findall(episodematch[0])

    programMeta = re.compile('<div class="program-meta">(.+?)</div>').findall(link)
    image = re.compile('<img src="(.+?)" alt').findall(programMeta[0])[0]

    topInfo = re.compile('<div class="top-info">(.+?)</div>').findall(link)
    channel = re.compile('<img src="(.+?)" width').findall(topInfo[0])
    if (len(channel) > 0):
        channel = 'ch' + channel[0][-5]
        if (channel == 'chv'):
            channel = 'chthaipbs'
    else:
        channel = 'chall'
    
    for episode in episodes:
        addThaiLink(episode[1].decode('tis-620'), seesantv + episode[0], 3, image, channel)
    # paginator
    discoverPagination(link, url)

def getVideoUrl(name, url, channel):
    trySD = True
    programId = re.compile('program_id=(\d+)').findall(url)[0]
    if (len(programId) < 5):
        programId = '0' + programId
    fullDate = re.compile('(\d+-\d+-\d+) ').findall(name)[0]
    date = ''.join(fullDate.splitlines()).replace('-','')
    hd = channel + '/' + programId + '/' + date + '1-' + programId + '.mp4'
    sd = channel + '/' + programId + '/' + date + '-' + programId + '.mp4'
    #for host in xrange(1, 31):
    for host in uk:
        #fullurl = "http://uk" + str (host) + ".seesantv.com/" + path
        fullurl = host + hd
        found = exists(fullurl)
        if (found):
            xbmc.Player().play(fullurl)
            trySD = False
            break
    if (trySD):
        for host in uk:
            fullurl = host + sd
            found = exists(fullurl)
            if (found):
                xbmc.Player().play(fullurl)
                break
'''
