# -*- coding: utf-8 -*-

import html.parser
import io, gzip, random, re
from resources.lib.tools import dom_parser

try:
    from urllib.request import Request, urlopen  # Python 3
except ImportError:
    from urllib2 import Request, urlopen  # Python 2


def request(url, headers=None, cookie=None, mobile=False, post=None, referer=None, compression=True, limit=None, xhr=False, timeout='30'):
    if url is None:
        return None

    if url.startswith('//'):
        url = 'http:' + url

    try:
        headers.update(headers)
    except:
        headers = {}

    if 'User-Agent' in headers:
        pass
    elif mobile is not True:
        headers['User-Agent'] = randomagent
    else:
        headers['User-Agent'] = 'Apple-iPhone/701.341'

    if 'Referer' in headers:
        pass
    elif referer is not None:
        headers['Referer'] = referer

    if 'Accept-Language' not in headers:
        headers['Accept-Language'] = 'en-US'

    if 'X-Requested-With' in headers:
        pass
    elif xhr is True:
        headers['X-Requested-With'] = 'XMLHttpRequest'

    if 'Cookie' in headers:
        pass
    elif cookie is not None:
        headers['Cookie'] = cookie

    if 'Accept-Encoding' in headers:
        pass
    elif compression and limit is None:
        headers['Accept-Encoding'] = 'gzip'

    request = Request(url, data=post)
    _add_request_header(request, headers)
    response = urlopen(request, timeout=int(timeout)).read()

    return response


def _basic_request(url, headers=None, post=None, timeout='30', limit=None):
    try:
        try:
            headers.update(headers)
        except:
            headers = {}

        request = Request(url, data=post)
        _add_request_header(request, headers)
        response = urlopen(request, timeout=int(timeout))
        return _get_result(response, limit)
    except:
        return


def _add_request_header(_request, headers):
    try:
        if not headers:
            headers = {}
        try:
            scheme = _request.get_type()
        except:
            scheme = 'http'

        referer = headers.get('Referer') if 'Referer' in headers else '%s://%s' % (scheme, _request.get_host())
        _request.add_unredirected_header('Host', _request.get_host())
        _request.add_unredirected_header('Referer', referer)

        for key in headers:
            _request.add_header(key, headers[key])
    except:
        return


def _get_result(response, limit=None):
    if limit == '0':
        result = response.read(224 * 1024)
    elif limit:
        result = response.read(int(limit) * 1024)
    else:
        result = response.read(5242880)

    try:
        encoding = response.info().getheader('Content-Encoding')
    except:
        encoding = None
    if encoding == 'gzip':
        result = gzip.GzipFile(fileobj=io.StringIO(result)).read()

    return result


def parseDOM(html, name='', attrs=None, ret=False):
    if attrs:
        attrs = dict((key, re.compile(value + ('$' if value else ''))) for key, value in attrs.items())
    results = dom_parser.parse_dom(html, name, attrs, ret)

    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]
    return results


def replaceHTMLCodes(txt):
    # Some HTML entities are encoded twice. Decode double.
    return _replaceHTMLCodes(_replaceHTMLCodes(txt))


def _replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = html.parser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = txt.strip()
    return txt


def randomagent():
    BR_VERS = [
        ['%s.0' % i for i in range(18, 50)],
        ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111',
         '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111', '40.0.2214.115',
         '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155',
         '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71', '46.0.2490.80', '46.0.2490.86',
         '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112', '50.0.2661.86', '51.0.2704.103',
         '52.0.2743.116', '53.0.2785.143', '54.0.2840.71', '61.0.3163.100', '63.0.3239.132', '78.0.3904.108'],
        ['11.0'],
        ['8.0', '9.0', '10.0', '10.6']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1',
                'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
                'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES),
                                  br_ver=random.choice(BR_VERS[index]))


def agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
