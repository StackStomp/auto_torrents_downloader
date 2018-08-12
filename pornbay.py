import re


def get_title(up):
    return "[Pornbay.org]"


def get_taddress_list(up):
    l = []
    for entry in up.get('entries', []):
        l.append(entry.link)
    return l


def get_title_list(up):
    l = []
    r = re.compile(r'\s*/\s*[fF]reeleech!?')
    for entry in up.get('entries', []):
        l.append(r.sub('', entry.title))
    return l
