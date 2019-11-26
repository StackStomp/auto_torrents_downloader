import signal
import feedparser
import re
import traceback
import logging
import socket
import requests

m_headers = {'User-Agent':'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

class TotalTimeout(Exception):
    pass
def timeout_handler(signum, frame):
    raise TotalTimeout("time out")
signal.signal(signal.SIGALRM, timeout_handler)


try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection


class Ipv4HTTPConnection(HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_INET)
        self.sock.connect((self.host, self.port, 0, 0))
        if self._tunnel_host:
            self._tunnel()


def read_url(url, timeout, protocol='ipv4'):
    if protocol == 'ipv4':
        requests.packages.urllib3.connectionpool.HTTPConnection = Ipv4HTTPConnection

    try:
        resp = requests.get(url, timeout=(max(timeout / 100, 10), timeout))
        if resp.status_code == 200:
            return resp.content
        else:
            return None
    except requests.exceptions.RequestException:
        logging.warning("Failed to open url {} because exception".format(url))
        logging.warning(traceback.format_exc())
        return None


class RSS(object):
    def __init__(self, cfg, db):
        self.url = cfg['address']
        self.url_timeout = cfg['feedurl-timeout']
        self.subscribers = cfg.get('subscribers', [])
        self.p = __import__(cfg['parser'])
        self.db = db
        self.matchers = cfg.get('filter',[])
        for matcher in self.matchers:
            if 'key-regex' not in matcher:
                continue
            for mre in matcher['key-regex']:
                re.compile('mre')

    def match_one(self, matcher, title):
        for kw in matcher.get('key-words', []):
            if kw not in title:
                return False, []
        matched_regex_str = []
        for krexp in matcher.get('key-regex', []):
            kr = re.compile(krexp)
            s = kr.search(title)
            if not s:
                return False, []
            matched_regex_str.append(s.group())
        return True, matcher.get('key-words', []) + matched_regex_str

    def match(self, title):
        for matcher in self.matchers:
            match_ret, match_str = self.match_one(matcher, title)
            if match_ret:
                return match_ret, match_str
        return False, []

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def get_feed_data(self):
        uc = read_url(self.url, self.url_timeout)
        if uc is None:
            return None

        return feedparser.parse(uc)

    def get_torrents_list(self):
        feeddata = self.get_feed_data()
        if not feeddata:
            logging.warning("Failed to get feed data from %s" % self.url)
            return None, None
        taddrs = self.p.get_taddress_list(feeddata)
        feedtitle = self.p.get_title(feeddata)
        ttitles = self.p.get_title_list(feeddata)

        if len(self.matchers) == 0:
            return taddrs, feedtitle

        tlist = []
        for i in range(0, len(taddrs)):
            matched, kwords = self.match(ttitles[i])
            if not matched:
                logging.debug("RSS torrent not matched, title %s, url %s" \
                                 %(ttitles[i], taddrs[i]))
                continue

            if self.db.binge_has_byurl(taddrs[i]):
                logging.debug("RSS torrent is exists in binge-list, url %s" % taddrs[i])
                continue

            keys = ';'.join(kwords)
            if self.db.binge_has_bykeys(keys):
                logging.info("RSS torrent(title %s) won't be downloaded because the keys exists %s"\
                    %(ttitles[i],keys))
                self.db.add_binge(taddrs[i], ttitles[i], keys, 0)
                continue

            logging.info("Torrent file %s, address %s need to be downloaded, key-words %s" \
                            %(ttitles[i], taddrs[i], keys))
            tlist.append(taddrs[i])
            self.db.add_binge(taddrs[i], ttitles[i], keys, 1)

        return tlist, feedtitle


def download_torrent(url, timeout):
    return read_url(url, timeout)
