import os
import sys
import getopt

help_info = '''
atd OPTIONS...
options:
  -p DIRECTORY     the path download torronts to
  -c CONFIG        the path to config file
  -d COMMAND       daemon mode start/stop/restart
  -b DIRECTORY     the database directory
'''

def print_help():
    print(help_info)

def check_config(config):
    #-c no need to check
    #-d
    if config['daemon']:
        if not config['daemon'] in \
            ('start','stop','restart'):
            print("Daemon command must be start, stop or restart")
            print_help()
            sys.exit(1)
        if config['daemon'] in ('stop','restart'):
            if not os.path.isfile(config['pid-file']):
                print("The pid file is not exists")
                print_help()
    #-p
    if not config.has_key('tdir'):
        print("Need torrents' directory")
        print_help()
        sys.exit(1)
    if not os.path.isdir(config['tdir']):
        print("The torrents' directory is not exists")
        print_help()
        sys.exit(1)
    #-a
    if not config.has_key('rss'):
        print("No rss feed's address found")
        print_help()
        sys.exit(1)
    for rss in config['rss']:
        if not rss.has_key('address'):
            print("The rss configuration need an address")
            print(rss)
            sys.exit(1)
        if not rss.has_key('parser'):
            print("The rss configuration need a parser")
            print(rss)
            sys.exit(1)
    #-b
    if not config.has_key('db'):
        print("No database path specified")
        print_help()
        sys.exit(1)

def get_config_fromjson(config, fdir):
    import json
    with open(fdir,'rb') as f:
        cf = json.load(f)
    if cf.has_key('torrent-dir'):
        config['tdir'] = os.path.abspath(cf['torrent-dir'])
    if cf.has_key('rss'):
        if type(cf['rss']) == list:
            if config.has_key('rss'):
                config['rss'] += cf['rss']
            else:
                config['rss'] = cf['rss']
        elif type(cf['rss']) == dict:
            if config.has_key('rss'):
                config['rss'].append(cf['rss'])
            else:
                config['rss'] = [cf['rss']]
        else:
            print("Unexpected rss info")
            print_help()
            sys.exit(1)
    if cf.has_key('db-dir'):
        config['db'] = os.path.abspath(cf['db-dir'])
    return config
    
def get_config():
    config = {'daemon':None, 
              'time':300, 
              'feedurl-timeout':30,
              'torurl-timeout':60,
              'db':os.path.abspath('atd.db'),
              'log-file':os.path.abspath('atdownloader.log'),
              'pid-file':os.path.abspath('atdownloader.pid'),
              'flush':True,
              'maxtry':10}
    shortopts = 'p:c:d:b:'
    try:
        optlist, args = getopt.getopt(sys.argv[1:], shortopts)
    except getopt.GetoptError as e:
        print(e)
        print_help()
        sys.exit(1)

    for key, value in optlist:
        if key == '-p':
            config['tdir'] = os.path.abspath(value)
        elif key == '-c':
            config = get_config_fromjson(config, value)
        elif key == '-d':
            config['daemon'] = value
        elif key =='-b':
            config['db'] = os.path.abspath(value)

    if os.path.isdir(config['db']):
        config['db'] = os.path.join(config['db'], 'atd.db')
    dbdir, dbname = os.path.split(config['db'])
    if dbdir != config['log-file']:
        config['log-file'] = os.path.join(dbdir, 'atdownloader.log')
        config['pid-file'] = os.path.join(dbdir, 'atdownloader.pid')

    check_config(config)

    #remove duplicates and import 
    new_rss = []
    for rss in config['rss']:
        for nr in new_rss:
            if nr['address'] == rss['address']:
                break
        else:
            rss['p'] = __import__(rss['parser'])
            new_rss.append(rss)
    config['rss'] = new_rss
    
    return config

if __name__ == '__main__':
    print("Begin ut...")
    print("    Test config file...")
    sys.argv = ['asd.py', '-c', 'cfg.json']
    cfg = get_config()
    assert cfg['tdir'] == '/home'
    assert 'http://test1.com' == cfg['rss'][0]['address']
    assert 'http://test2.com' == cfg['rss'][1]['address']
    assert len(cfg['rss']) == 2
    assert cfg['daemon'] == None
    assert cfg['db'] == '/home/test1.db'
    assert cfg['log-file'] == '/home/atdownloader.log'
    assert cfg['pid-file'] == '/home/atdownloader.pid'

    print("    Test cfg1.json...")
    sys.argv = ['asd.py', '-c', 'cfg1.json', '-d', 'start']
    cfg = get_config()
    assert cfg['tdir'] == '/home'
    assert 'http://test1.com' == cfg['rss'][0]['address']
    assert len(cfg['rss']) == 1
    assert cfg['daemon'] == 'start'
    assert cfg['db'] == '/home/atd.db'
    assert cfg['log-file'] == '/home/atdownloader.log'
    assert cfg['pid-file'] == '/home/atdownloader.pid'
