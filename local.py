import sqlite3

class UndownDB(object):
    def init_undown(self):
        c = self.db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS undown \
            (url text, trydown integer, title text, subscriber text)")

    def add_undown(self, tor_url, title, subscribers):
        c = self.db.cursor()
        c.execute("INSERT INTO undown (url, trydown, title, subscriber) VALUES (?,0,?,?)", \
            (tor_url, title, ' '.join(subscribers)))

    def undown_has_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT * FROM undown WHERE url = (?)",(tor_url,))
        if c.fetchall():
            return True
        return False

    def undown_delete_byurl(self, tor_url):
        if not self.undown_has_byurl(tor_url):
            raise Exception("the torents is not exists in undown table")
        c = self.db.cursor()
        c.execute("DELETE FROM undown WHERE url = (?)", (tor_url,))

    def get_subscribers(self, tor_url):
        if not self.undown_has_byurl(tor_url):
            return None
        c = self.db.cursor()
        c.execute("SELECT subscriber FROM undown WHERE url = (?)", (tor_url,))
        r = c.fetchall()
        assert (len(r) == 1)
        subscriber = r[0][0]
        return subscriber.split()

    def get_trydowntimes_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT trydown FROM undown WHERE url = (?)",(tor_url,))
        times = c.fetchall()
        if times:
            times = int(times[0][0])
        return times

    def plustrydowntimes_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT trydown FROM undown WHERE url = (?)",(tor_url,))
        times = c.fetchall()
        if not times:
            raise Exception("Can not find the torrent by url %s" %tor_url)
        times = int(times[0][0])
        c.execute("UPDATE undown SET trydown = (?) WHERE url = (?)", \
                (times+1,tor_url))

    def get_title(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT title FROM undown WHERE url = (?)", (tor_url,))
        title = c.fetchall()
        if len(title) > 0:
            return title[0][0]
        else:
            return None

    def get_undown(self):
        c = self.db.cursor()
        c.execute("SELECT url,title FROM undown")
        r = c.fetchall()
        undown_list = []
        for tor in r:
            undown_list.append({'url':tor[0], 'title':tor[1]})
        return undown_list

class DownDB(object):
    def init_torrents(self):
        c = self.db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS torrents \
            (url text, md5 text, name text)")

    def add_exists(self, name, md5):
        c = self.db.cursor()
        c.execute("INSERT INTO torrents (md5, name) VALUES (?,?)", \
            (md5, name))

    def add_down(self, url, name, md5):
        c = self.db.cursor()
        c.execute("INSERT INTO torrents (url, md5, name) VALUES (?,?,?)",\
                    (url, md5, name))
        

    def down_has_byurl(self, tor_url):
        c = self.db.cursor()
        c.execute("SELECT * FROM torrents WHERE url = (?)",(tor_url,))
        if c.fetchall():
            return True
        return False
    
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

class BingeDB(object):
    def init_binge(self):
        sor = self.db.cursor()
        sor.execute("CREATE TABLE IF NOT EXISTS binge \
            (url text, title text, keys text, downloaded integer)")
    def binge_has_byurl(self, url):
        sor = self.db.cursor()
        sor.execute("SELECT * FROM binge WHERE url = (?)", (url,))
        if sor.fetchall():
            return True
        else:
            return False
    def binge_has_bykeys(self, keys):
        sor = self.db.cursor()
        sor.execute("SELECT * FROM binge WHERE keys = (?)", (keys,))
        if sor.fetchall():
            return True
        else:
            return False
    def add_binge(self, url, title, keys, downloaded):
        sor = self.db.cursor()
        sor.execute("INSERT INTO binge (url, title, keys, downloaded) \
            VALUES (?,?,?,%d)" % downloaded, (url, title, keys))

class LocalTorrents(UndownDB, DownDB, BingeDB):
    def __init__(self, db):
        self.db = sqlite3.connect(db)
        self.init_torrents()
        self.init_undown()
        self.init_binge()

    def __del__(self):
        if self.db:
            self.close()

    def close(self):
        self.db.commit()
        self.db.close()
        self.db = None

    def has_byurl(self, tor_url):
        if self.undown_has_byurl(tor_url):
            return True
        if self.down_has_byurl(tor_url):
            return True
        return False

    def set_downloaded(self, tor_url, name, md5):
        if self.undown_has_byurl(tor_url):
            self.undown_delete_byurl(tor_url)
        if not self.down_has_byurl(tor_url):
            self.add_down(tor_url, name, md5)
