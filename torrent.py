import bencode

def get_name(tfile):
    with open(tfile,'rb') as f:
        b = bencode.bdecode(f.read())
    return b['info']['name']

if __name__ == '__main__':
    name = get_name('test.torrent')
    assert len(name) > 0
    print name
