#!/usr/bin/python
import os
import urllib2
import shell
import local
import hashlib
import torrent
import daemon

opt = shell.get_config()

if opt['daemon']:
    daemon.daemon_exec(opt)

print("Configuration:")
for key in opt:
    print("%s:%s"%(key,opt[key]))
    
db = local.LocalTorrents(opt['db'])

#read in all torrents exists to the db
if opt['flush']:
    print("Scan dir %s, and record torrents..." % opt['tdir'])
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
        print("Added exists torrent file %s, md5 %s" \
                % (tname, md5))

def get_feed_data(url, timeout):
    import feedparser
    try:
        u = urllib2.urlopen(url, timeout=timeout)
    except urllib2.URLError:
        print("Failed to open url %s, timeout %d, timeout maybe" % (url, timeout))
        return None
    uc = u.read()
    u.close()
    return feedparser.parse(uc)

def download_torrent(url, timeout):
    try:
        u = urllib2.urlopen(url, timeout=timeout)
    except IOError:
        print("Failed to download torrent from %s, invalid url" % url)
        return None
    except urllib2.URLError:
        print("Failed to download torrent from %s, timeout %d, timeout maybe" \
            % (url, timeout))
        return None
    uc = u.read()
    u.close()
    return uc

def download():
    #Add new torrents' addresses to db
    for rss in opt['rss']:
        feeddata = get_feed_data(rss['address'], opt['feedurl-timeout'])
        if not feeddata:
            print("Failed to get feed data from %s" % rss['address'])
            continue
        feedtitle = rss['p'].get_title(feeddata)
        tlist = rss['p'].get_torrents_list(feeddata)
        for taddr in tlist:
            if db.has_byurl(taddr):
                continue
            print("Add new torrent to db, address %s" % taddr)
            db.add(taddr)
    
    #Download torrents undownloaded
    tlist = db.get_undown()
    for taddr in tlist:
        print "Begin to download torrent from", taddr
        if db.get_trydowntimes_byurl(taddr) >= opt['maxtry']:
            continue
        db.plustrydowntimes_byurl(taddr)
    
        tdata = download_torrent(taddr, opt['torurl-timeout'])
        if not tdata:
            print("Can not get data fro address %s"%taddr)
            continue
    
        tname = torrent.get_name(tdata)
        if not tname:
            print("Invalid torrent data")
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
    
        print "Torrent file has been downloaded, name", tfname
        with open(os.path.join(opt['tdir'], tfname), 'w') as f:
            f.write(tdata)
        db.set_name(taddr, tname)
        db.set_md5(taddr, md5)
        db.set_downloaded(taddr)

if not opt['daemon']:
    import sys
    download()
    print "hello"
    sys.exit(0)

while True:
    import time
    download()
    time.sleep(opt['time'])

