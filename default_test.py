#!/usr/bin/python
import sys
import urllib2
import feedparser


m_headers = {'User-Agent':'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}


if len(sys.argv) == 2:
    url = sys.argv[1]
    parser_name = "default"
elif len(sys.argv) == 3:
    parser_name = sys.argv[1]
    url = sys.argv[2]
else:
    print("Format: %s [parser-name] <rss-url>" % sys.argv[0])
    sys.exit(1)


parser = __import__(parser_name)


req = urllib2.Request(url,headers=m_headers)
u = urllib2.urlopen(req)
uc = u.read()
u.close()

up = feedparser.parse(uc)
print("The default analyse result:")
print 'Title:', parser.get_title(up)
addrs = parser.get_taddress_list(up)
titles = parser.get_title_list(up)

print addrs
print titles

if len(addrs) == 0 and len(titles) == 0:
    print("Can not pick torrent's name or address out from url %s" % url)
    print("Add torrent(s) to your RSS-feeds before test")
    print("If there are torrent(s) in your RSS-feeds, that means the default-analyser can not analyse your RSS-feeds")
    sys.exit(0)

if len(addrs) != len(titles):
    print("Failed to analyse by default-analyser")
    print "Titles(%d):", (len(titles), titles)
    print "Addresses(%d)", (len(addrs), addrs)
    sys.exit(0)

for i in range(0, len(titles)):
    print "Name: %s; Address: %s" % (titles[i], addrs[i])
