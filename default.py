def get_taddress_list(up):
	l = []
	for entry in up.get('entries', []):
		for link in entry.get('links', []):
			if link.get('type','') == 'application/x-bittorrent':
				l.append(link.get('href',''))
	return l

def get_ttitle_list(up):
	l = []
	for entry in up.get('entries', []):
		l.append(entry.get('title', ''))
	return l

def get_title(up):
    if not up.has_key('feed'):
        return None
    if not up['feed'].has_key('title'):
        return None
    return up['feed']['title']
