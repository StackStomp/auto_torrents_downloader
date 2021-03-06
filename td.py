#! /usr/bin/python
import os
import shell
import local
import hashlib
import torrent
import daemon
import logging
import ptserver
import publisher

def download():
    #read the rss, and add new torrent-addresses to db
    for rss in rsss:
        logging.debug("Begin to read from rss %s" % rss.url)
        tlist, ttitle = rss.get_torrents_list()
        if not tlist:
            continue
        for taddr in tlist:
            if db.has_byurl(taddr):
                logging.debug("New torrent exists, address %s" % taddr)
                continue
            logging.info("Add new torrent to db, address %s" % taddr)
            db.add_undown(taddr, ttitle, rss.subscribers)

    #Download torrents undownloaded
    publish_task = {}
    tlist = db.get_undown()
    for tor in tlist:
        taddr = tor['url']
        feedtitle = tor['title']
        if db.get_trydowntimes_byurl(taddr) >= opt['maxtry']:
            logging.debug("The retry-download-times of torrent %s, addr %s exceeds the max retry limit %d, skip it" % (feedtitle, taddr, opt['maxtry']))
            continue
        logging.info("Begin to download torrent from %s"% taddr)
        db.plustrydowntimes_byurl(taddr)

        tdata = ptserver.download_torrent(taddr, opt['torurl-timeout'])
        if not tdata:
            logging.warning("Can not get data fro address %s"%taddr)
            continue

        tname = torrent.get_name(tdata)
        if not tname:
            logging.warning("Invalid torrent data")
            continue
        tfname ="[%s] %s.torrent" %(feedtitle, tname)

        md5 = hashlib.md5(tdata).hexdigest()

        if db.has_byname(tname):
            logging.warning("New torrents exists by name, addr %s, name %s, md5 %s"\
                        % (taddr, tname, md5))
            db.set_downloaded(taddr, tname, md5)
            continue
        if db.has_bymd5(md5):
            logging.warning("New torrents exists by md5, addr %s, name %s, md5 %s"\
                        % (taddr, tname, md5))
            db.set_downloaded(taddr, tname, md5)
            continue

        logging.info("Torrent file has been downloaded, name %s"%tfname)
        subscriber_list = db.get_subscribers(taddr)
        for ser in subscriber_list:
            if ser in publish_task:
                publish_task[ser].append(tfname)
            else:
                publish_task[ser] = [tfname]
        with open(os.path.join(opt['tdir'], tfname), 'wb') as f:
            f.write(tdata)
        db.set_downloaded(taddr, tname, md5)

    return publish_task


# Init the level of the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# get config
opt = shell.get_config()

if opt['daemon']:
    daemon.daemon_exec(opt)

    # redirect logs to the log file in the daemon mode
    from logging.handlers import RotatingFileHandler
    ch = RotatingFileHandler(opt['log-file'], maxBytes=20*1024*1024, backupCount=10)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    root_logger.handlers = []
    root_logger.addHandler(ch)
    root_logger.debug("The logger has been initialized")

# print configuration
logging.info("Configuration:")
for key in opt:
    logging.info("%s:%s"%(key,opt[key]))

# init torrents' database
db = local.LocalTorrents(opt['db'])

# read in all torrents exists to the db
if opt['flush']:
    for tdir in opt['tdirs']:
        logging.info("Scan dir %s, and record torrents..." % tdir)
        for f in os.listdir(tdir):
            fullf = os.path.join(tdir, f)
            if not os.path.isfile(fullf):
                continue
            tname = torrent.get_tname_byfname(f)
            if not tname:
                continue
            if db.has_byname(tname):
                continue
            md5 = hashlib.md5(open(fullf,'rb').read()).hexdigest()
            db.add_exists(tname, md5)

            logging.info("Added exists torrent file %s, md5 %s" % (tname, md5))

# Init all RSS
rsss = []
for rss_cfg in opt['rss']:
    rss = ptserver.RSS(rss_cfg, db)

    if 'subscriber' in rss_cfg:
        if type(rss_cfg['subscriber']) == list:
            rss.subscribers = rss_cfg['subscriber']
        else:
            rss.add_subscriber(rss_cfg['subscriber'])
    rsss.append(rss)
    logging.info("Read in rss-feed config, addr %s, timeout %d/%d"\
                %(rss_cfg['address'], opt['feedurl-timeout'], opt['torurl-timeout']))

# #console mode, run only on time
# if not opt['daemon']:
# import sys
# logging.debug("Running in console mode")
# download()
# sys.exit(0)

# run inifitely
cnt = 0
while True:
    import time
    cnt += 1
    tm = time.gmtime()
    logging.debug("Run %d times, begin to download" % cnt)
    ptask = download()
    #publish if needed
    if len(ptask) > 0:
        logging.info("Publish task info %s" %ptask)
        for subscriber in ptask:
            publisher.publish_tordown([subscriber], ptask[subscriber])
    time.sleep(opt['time'])
