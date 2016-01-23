import os
import bencode
import re

def get_name(tdata):
    try:
        b = bencode.bdecode(tdata)
    except bencode.BTL.BTFailure:
        return None
    return b['info']['name']

hre = re.compile(r'\[\w+\]\s?(?P<tname>[\s\S]+)')
def get_tname_byfname(file_name, heads=[]):
    tname, ext = os.path.splitext(file_name)
    if ext == '.added':
        tname,ext = os.path.splitext(tname)
    if ext != '.torrent':
        return None

    if tname[:2] == "._":
        tname = tname[2:]

    hm = hre.match(tname)
    if hm:
        tname = hm.group('tname')

    for head in heads:
        if tname.startswith(head):
            tname = tname[len(head):].lstrip()
    return tname


if __name__ == '__main__':
    with open('test.torrent','rb') as f:
        name = get_name(f.read())
    assert len(name) > 0
    print name

    tname = get_tname_byfname('hello.torrent')
    assert tname == 'hello'
    tname = get_tname_byfname('[TTG] hello.torrent', heads=['[TTG]',])
    assert tname == 'hello'
    tname = get_tname_byfname('[TTG] hello.torrent.added', heads=['[TTG]'])
    assert tname == 'hello'
    tname = get_tname_byfname('._[TTG] hello.torrent.added', heads=['[TTG]'])
    assert tname == 'hello'
    tname = get_tname_byfname('[TTG] hello.torrent.added', heads=None)
    assert tname == 'hello'
    tname = get_tname_byfname('[HDR] hello.torrent.added', heads=None)
    assert tname == 'hello'
    tname = get_tname_byfname('hello.torrent.added', heads=None)
    assert tname == 'hello'
    tname = get_tname_byfname('[OpenCD]hello.torrent.added', heads=None)
    assert tname == 'hello'
