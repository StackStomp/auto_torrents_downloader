#!/usr/bin/python
import os
import urllib2
import shell
import local
import hashlib
import torrent
import daemon
import logging
import feedparser
import signal

# create logger
logger = logging.getLogger('td')
logger.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# 'application' code
logger.debug('logger ok')
#logger.info('info message')
#logger.warn('warn message')
#logger.error('error message')
#logger.critical('critical message')

opt = shell.get_config()

if opt['daemon']:
    daemon.daemon_exec(opt)

logger.info("Configuration:")
for key in opt:
    logger.info("%s:%s"%(key,opt[key]))
    
db = local.LocalTorrents(opt['db'])

#read in all torrents exists to the db
if opt['flush']:
    logger.info("Scan dir %s, and record torrents..." % opt['tdir'])
    for f in os.listdir(opt['tdir']):
        fullf = os.path.join(opt['tdir'], f)
        if not os.path.isfile(fullf):
            continue
        tname = torrent.get_tname_byfname(f)
        if not tname:
            continue
        if db.has_byname(tname):
            continue
        md5 = hashlib.md5(open(fullf,'rb').read()).hexdigest()
        db.add_exists(tname, md5)
#        try:
#            tname = tname.encode('utf-8')
#        except UnicodeDecodeError:
#            pass
        logger.info("Added exists torrent file %s, md5 %s" \
                % (tname, md5))

def timeout_handler(signum, frame):
    raise urllib2.URLError("time out")
signal.signal(signal.SIGALRM, timeout_handler)

def get_feed_data(url, timeout):
    signal.alarm(timeout)
    try:
        #can not use the argument timeout applied by urlopen
        #because the timeout argument is 'defaulttimeout'
        #but we need a whole-procedure-timeout
        u = urllib2.urlopen(url)
        uc = u.read()
        u.close()
    except urllib2.URLError:
        logger.warn("Failed to open url %s, timeout %d, timeout maybe" % (url, timeout))
        return None
    signal.alarm(0)

    return feedparser.parse(uc)

def download_torrent(url, timeout):
    signal.alarm(timeout)
    try:
        u = urllib2.urlopen(url)
        uc = u.read()
        u.close()
    except IOError:
        logger.error("Failed to download torrent from %s, invalid url" % url)
        return None
    except urllib2.URLError:
        logger.warn("Failed to download torrent from %s, timeout %d, timeout maybe" \
            % (url, timeout))
        return None
    signal.alarm(0)
    return uc

def download():
    #Add new torrents' addresses to db
    for rss in opt['rss']:
        feeddata = get_feed_data(rss['address'], opt['feedurl-timeout'])
        if not feeddata:
            logger.warn("Failed to get feed data from %s" % rss['address'])
            continue
        feedtitle = rss['p'].get_title(feeddata)
        tlist = rss['p'].get_torrents_list(feeddata)
        for taddr in tlist:
            if db.has_byurl(taddr):
                logger.debug("New torrent exists, address %s" % taddr)
                continue
            logger.info("Add new torrent to db, address %s" % taddr)
            db.add(taddr)
    
    #Download torrents undownloaded
    tlist = db.get_undown()
    for taddr in tlist:
        logger.info("Begin to download torrent from %s"% taddr)
        if db.get_trydowntimes_byurl(taddr) >= opt['maxtry']:
            continue
        db.plustrydowntimes_byurl(taddr)
    
        tdata = download_torrent(taddr, opt['torurl-timeout'])
        if not tdata:
            logger.warn("Can not get data fro address %s"%taddr)
            continue
    
        tname = torrent.get_name(tdata)
        if not tname:
            logger.warn("Invalid torrent data")
            continue
    
        if type(feedtitle) != type(tname):
            #We convert to the same encoding, because:
            #http://jerrypeng.me/2012/03/python-unicode-format-pitfall/
            if type(feedtitle) == str:
                feedtitle = feedtitle.decode('utf-8')
            if type(tname) == str:
                tname = tname.decode('utf-8')
        tfname ="[%s] %s.torrent" %(feedtitle, tname)
    
        md5 = hashlib.md5(tdata).hexdigest()
    
        logger.info("Torrent file has been downloaded, name %s"%tfname)
        with open(os.path.join(opt['tdir'], tfname), 'w') as f:
            f.write(tdata)
        db.set_name(taddr, tname)
        db.set_md5(taddr, md5)
        db.set_downloaded(taddr)

if not opt['daemon']:
    import sys
    logger.debug("Running in console mode")
    download()
    sys.exit(0)

cnt = 0
while True:
    import time
    cnt += 1
    tm = time.gmtime()
    logger.debug("Run %d times, begin to download" % cnt)
    download()
    time.sleep(opt['time'])

