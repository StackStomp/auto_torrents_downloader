import feedparser

addr = 'totheglory.im'
head = '[TTG]'

def get_torrents_list(up):
    #u = urllib.urlopen(addr)
    #uc = u.read()
    #up = feedparser.parse(uc)
    if not up.has_key('entries'):
        return []
    if len(['entries']) == 0:
        return []
    l = []
    for entry in up['entries']:
        l.append(entry['link'])
    return l
    
def get_title(up):
    if not up.has_key('feed'):
        return None
    if not up['feed'].has_key('title'):
        return None
    return up['feed']['title']

if __name__ == '__main__':
    print "Unit test..."
    import urllib
    url = 'https://totheglory.im/putrssmc.php?par===&ssl=yes'
    print "Open and read url", url
    u = urllib.urlopen(url)
    uc = u.read()
    u.close()
    up = feedparser.parse(uc)
    print "Get torrents list."
    print get_torrents_list(up)
    print "Get torrents title."
    print get_title(up)
