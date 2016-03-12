#!/usr/bin/python
import os
import shell
import local
import hashlib
import torrent
import daemon
import logging
import ptserver

def download():
    #read the rss, and add new torrent-addresses to db
    for rss in rsss:
        tlist = rss.get_torrents_list()
        if not tlist:
            continue
        for taddr in tlist:
            if db.has_byurl(taddr):
                logger.debug("New torrent exists, address %s" % taddr)
                continue
            logger.info("Add new torrent to db, address %s" % taddr)
            db.add(taddr)
    
    #Download torrents undownloaded
    down_list = []
    tlist = db.get_undown()
    for taddr in tlist:
        logger.info("Begin to download torrent from %s"% taddr)
        if db.get_trydowntimes_byurl(taddr) >= opt['maxtry']:
            continue
        db.plustrydowntimes_byurl(taddr)
    
        tdata = ptserver.download_torrent(taddr, opt['torurl-timeout'], logger)
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
        down_list.append(tfname)
        with open(os.path.join(opt['tdir'], tfname), 'w') as f:
            f.write(tdata)
        db.set_name(taddr, tname)
        db.set_md5(taddr, md5)
        db.set_downloaded(taddr)

    return down_list

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

#get config
opt = shell.get_config()

#daemon operation
if opt['daemon']:
    daemon.daemon_exec(opt)

#print configuration
logger.info("Configuration:")
for key in opt:
    logger.info("%s:%s"%(key,opt[key]))
    
#init torrents' database
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

#Init all RSS
rsss = []
for rss_cfg in opt['rss']:
    rss = ptserver.RSS(rss_cfg['address'], opt['feedurl-timeout'], 
                       opt['torurl-timeout'], rss_cfg['p'],logger)

    if rss_cfg.has_key('subscriber'):
        if type(rss_cfg['subscriber']) == list:
            rss.subscribers = rss_cfg['subscriber']
        else:
            rss.add_subscriber(rss_cfg['subscriber'])
    rsss.append(rss)
    logger.info("Read in rss-feed config, addr %s, timeout %d/%d"\
                %(rss_cfg['address'], opt['feedurl-timeout'],\
                opt['torurl-timeout']))

#console mode, run only on time
if not opt['daemon']:
    import sys
    logger.debug("Running in console mode")
    download()
    sys.exit(0)

#daemon mode, run inifitely
cnt = 0
while True:
    import time
    cnt += 1
    tm = time.gmtime()
    logger.debug("Run %d times, begin to download" % cnt)
    dlist = download()
    if len(dlist) > 0:
        #send notificationg email when daemon mode
        pass
    time.sleep(opt['time'])

