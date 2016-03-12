import sqlite3

class LocalTorrents:
    def __init__(self, db):
        self.db = sqlite3.connect(db)
        c = self.db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS torrents \
            (url text, md5 text, \
             name text, trydown integer, \
             downloaded integer, title text)")
    def __del__(self):
        if self.db:
            self.close()

    def close(self):
        self.db.commit()
        self.db.close()
        self.db = None

    def add_exists(self, name, md5):
        c = self.db.cursor()
        c.execute("INSERT INTO torrents (md5, name, downloaded) VALUES (?,?,1)", \
            (md5, name))
    def add(self, tor_url):
        c = self.db.cursor()
        c.execute("INSERT INTO torrents (url, trydown, downloaded) VALUES (?,0,0)", \
            (tor_url,))
    def has_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT * FROM torrents WHERE url = (?)",(tor_url,))
        if c.fetchall():
            return True
        else:
            return False

    def get_trydowntimes_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT trydown FROM torrents WHERE url = (?)",(tor_url,))
        times = c.fetchall()
        if times:
            times = int(times[0][0])
        return times
    def plustrydowntimes_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT trydown FROM torrents WHERE url = (?)",(tor_url,))
        times = c.fetchall()
        if not times:
            raise Exception("Can not find the torrent by url %s" %tor_url)
        times = int(times[0][0])
        c.execute("UPDATE torrents SET trydown = (?) WHERE url = (?)", \
                (times+1,tor_url))

    def set_name(self, tor_url, name):
        c = self.db.cursor()
        c.execute("UPDATE torrents SET name = (?) WHERE url = (?)", \
            (name, tor_url))
    def has_byname(self, name):
        c = self.db.cursor()
        c.execute("SELECT * FROM torrents WHERE name = (?)", (name,))
        if c.fetchall():
            return True
        else:
            return False

    def set_title(self, tor_url, title):
        c = self.db.cursor()
        c.execute("UPDATE torrents SET title = (?) WHERE url = (?)", \
            (title, tor_url))
    def get_title(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT title FROM torrents WHERE url = (?)", (tor_url,))
        title = c.fetchall()
        if len(title) > 0:
            return title[0]
        else:
            return None

    def set_md5(self, tor_url, md5):
        c = self.db.cursor()
        c.execute("UPDATE torrents SET md5 = (?) WHERE url = (?)", \
            (md5, tor_url))
    def has_bymd5(self, md5):
        c = self.db.cursor()
        c.execute("SELECT * FROM torrents WHERE md5 = (?)", (md5,))
        if c.fetchall():
            return True
        else:
            return False

    def set_downloaded(self, tor_url):
        c = self.db.cursor()
        c.execute("UPDATE torrents SET downloaded = 1 WHERE url = (?)", \
            (tor_url,))
    def get_undown(self):
        c = self.db.cursor()
        c.execute("SELECT url,title FROM torrents WHERE downloaded = 0")
        r = c.fetchall()
        undown_list = []
        for tor in r:
            undown_list.append({'url':tor[0], 'title':tor[1]})
        return undown_list
            

if __name__ == '__main__':
    print "Begin to LocalTorrents ut..."
    import os
    if os.path.isfile("test.db"):
        os.remove("test.db")
    l = LocalTorrents(":memory:")
    ba = r'https://totheglory.im/rssdd.php?par=hello=='

    print "    Test adding torrents..."
    for i in range(1,11):
        l.add(ba+str(i))
    undown = l.get_undown()
    assert len(undown) == 10
    for i in range(1,11):
        assert (ba+str(i)) in undown
    for i in range(1,21):
        if i < 11:
            assert l.has_byurl(ba+str(i))
        else:
            assert not l.has_byurl(ba+str(i))

    print "    Test update try down times"
    for i in range(1,11):
        t = l.get_trydowntimes_byurl(ba+str(i))
        assert t == 0
        l.plustrydowntimes_byurl(ba+str(i))
    for i in range(1,11):
        t = l.get_trydowntimes_byurl(ba+str(i))
        assert t == 1

    print "    Test setting downloaded..."
    for i in range(1,6):
        l.set_downloaded(ba+str(i))
    undown = l.get_undown()
    assert len(undown) == 5
    for i in range(1,11):
        if i < 6:
            assert (ba+str(i)) not in undown
        else:
            assert (ba+str(i)) in undown

    print "    Test adding and getting md5..."
    bm = '537d03e06e3384bee77853c4911d760'
    for i in range(1,6):
        l.set_md5(ba+str(i), bm+str(i))
    for i in range(1,11):
        if i < 6:
            assert l.has_bymd5(bm+str(i))
        else:
            assert not l.has_bymd5(bm+str(i))

    print "    Test adding and getting name..."
    bn = "torrent_name"
    for i in range(6,11):
        l.set_name(ba+str(i), bn+str(i)+".torrent")
    for i in range(1,11):
        if i < 6:
            assert not l.has_byname(bn+str(i)+".torrent")
        else:
            assert l.has_byname(bn+str(i)+".torrent")

    print "    Test adding exists..."
    prev_undown = l.get_undown()
    for i in range(11,21):
        l.add_exists(bn+str(i)+".torrent", bm+str(i))
    undown = l.get_undown()
    assert len(prev_undown) == len(undown)
    for  i in range(11,21):
        assert l.has_byname(bn+str(i)+".torrent")
        assert l.has_bymd5(bm+str(i))
    l.close()
