import signal
import urllib2
import httplib
import feedparser
import re

class TotalTimeout(Exception):
    pass
def timeout_handler(signum, frame):
    raise TotalTimeout("time out")
signal.signal(signal.SIGALRM, timeout_handler)

class RSS(object):
    def __init__(self, cfg, logger, db):
        self.url = cfg['address']
        self.url_timeout = cfg['feedurl-timeout']
        self.subscribers = cfg.get('subscribers', [])
        self.p = __import__(cfg['parser'])
        self.logger = logger
        self.db = db
        self.matchers = cfg.get('filter',[])
        for matcher in self.matchers:
            if not matcher.has_key('key-regex'):
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
        signal.alarm(self.url_timeout)
        try:
            #can not use the argument timeout applied by urlopen
            #because the timeout argument is 'defaulttimeout'
            #but we need a whole-procedure-timeout
            u = urllib2.urlopen(self.url)
            uc = u.read()
            u.close()
        except TotalTimeout:
            self.logger.warn("Failed to open url %s, timeout %d"\
                            % (self.url, self.url_timeout))
            return None
        except urllib2.URLError, e:
            signal.alarm(0)
            self.logger.warn("Failed to open url %s because urllib2.URLError, info %s" \
                        % (self.url, e))
            return None
        except httplib.IncompleteRead, e:
            signal.alarm(0)
            self.logger.warn("Failed to open url %s because httplib.IncompleteRead, info %s" \
                        % (self.url, e))
            return None
        except httplib.BadStatusLine, e:
            signal.alarm(0)
            self.logger.warn("Failed to open url %s because httplib.BadStatusLine, info %s" \
                        % (self.url, e))
            return None

        signal.alarm(0)
    
        return feedparser.parse(uc)

    def get_torrents_list(self):
        feeddata = self.get_feed_data()
        if not feeddata:
            self.logger.warn("Failed to get feed data from %s" % self.url)
            return None, None
        taddrs = self.p.get_taddress_list(feeddata)
        feedtitle = self.p.get_title(feeddata)
        ttitles = self.p.get_ttitle_list(feeddata)

        if len(self.matchers) == 0:
            return taddrs, feedtitle

        tlist = []
        for i in range(0, len(taddrs)):
            matched, kwords = self.match(ttitles[i])
            if not matched:
                self.logger.debug("RSS torrent not matched, title %s, url %s" \
                                 %(ttitles[i], taddrs[i]))
                continue

            if self.db.binge_has_byurl(taddrs[i]):
                self.logger.debug("RSS torrent is exists in binge-list, url %s" % taddrs[i])
                continue

            keys = ';'.join(kwords)
            if self.db.binge_has_bykeys(keys):
                self.logger.info("RSS torrent(title %s) won't be downloaded because the keys exists %s"\
                    %(ttitles[i],keys))
                self.db.add_binge(taddrs[i], ttitles[i], keys, 0)
                continue

            self.logger.info("Torrent file %s, address %s need to be downloaded, key-words %s" \
                            %(ttitles[i], taddrs[i], keys))
            tlist.append(taddrs[i])
            self.db.add_binge(taddrs[i], ttitles[i], keys, 1)

        return tlist, feedtitle
        
    
def download_torrent(url, timeout, logger):
    signal.alarm(timeout)
    try:
        u = urllib2.urlopen(url)
        uc = u.read()
        u.close()
    except IOError:
        logger.error("Failed to download torrent from %s, invalid url" % url)
        return None
    except TotalTimeout:
        logger.warn("Failed to open url %s, timeout %d" % (url, timeout))
        return None
    except urllib2.URLError, e:
        signal.alarm(0)
        logger.warn("Failed to open url %s because urllib2.URLError, info %s" \
                    % (url, e))
        return None
    except httplib.IncompleteRead, e:
        signal.alarm(0)
        logger.warn("Failed to open url %s because httplib.IncompleteRead, info %s" \
                    % (url, e))
        return None
    except httplib.BadStatusLine, e:
        signal.alarm(0)
        logger.warn("Failed to open url %s because httplib.BadStatusLine, info %s" \
                    % (self.url, e))
        return None

    signal.alarm(0)
    return uc


