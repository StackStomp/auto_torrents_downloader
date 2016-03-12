import signal
import urllib2
import feedparser

class TotalTimeout(Exception):
    pass
def timeout_handler(signum, frame):
    raise TotalTimeout("time out")
signal.signal(signal.SIGALRM, timeout_handler)

class RSS(object):
    def __init__(self, url, url_timeout, download_timeout, parser, logger):
        self.url = url
        self.url_timeout = url_timeout
        self.download_timeout = download_timeout
        self.subscribers = []
        self.p = parser
        self.logger = logger

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
        signal.alarm(0)
    
        return feedparser.parse(uc)

    def get_torrents_list(self):
        feeddata = self.get_feed_data()
        if not feeddata:
            self.logger.warn("Failed to get feed data from %s" % self.url)
            return None, None
        feedtitle = self.p.get_title(feeddata)
        tlist = self.p.get_torrents_list(feeddata)
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
    signal.alarm(0)
    return uc


