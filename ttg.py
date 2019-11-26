import feedparser

addr = 'totheglory.im'
head = '[TTG]'


def get_torrents_list(up, key):
    l = []
    for entry in up.get('entries', []):
        l.append(entry.get(key, ''))
    return l


def get_taddress_list(up):
    return get_torrents_list(up, 'link')


def get_title_list(up):
    return get_torrents_list(up, 'title')


def get_title(up):
    return up.get('feed', {}).get('title', None)

