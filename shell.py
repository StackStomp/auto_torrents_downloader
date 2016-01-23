import os
import sys
import getopt

help_info = '''
atd OPTIONS...
options:
  -p DIRECTORY     the path download torronts to
  -c CONFIG        the path to config file
  -d               daemon mode
  -a ADDRESS       rss feed address
  -b DIRECTORY     the database directory
'''

def print_help():
    print(help_info)

def check_config(config):
    #-c,-d no need to check
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
    #-b
    if not config.has_key('db'):
        print("No database path specified")
        print_help()
        sys.exit(1)

def get_config_fromjson(config, fdir):
    import json
    with open(fdir,'rb') as f:
        cf = json.load(f)
    if cf.has_key('p'):
        config['tdir'] = cf['p']
    if cf.has_key('d'):
        if cf['d'] != 0:
            config['daemon'] = True
    if cf.has_key('a'):
        if type(cf['a']) == list:
            if config.has_key('rss'):
                config['rss'] += cf['a']
            else:
                config['rss'] = cf['a']
        else:
            if config.has_key('rss'):
                config['rss'].append(cf['a'])
            else:
                config['rss'] = [cf['a']]
    if cf.has_key('b'):
        config['db'] = os.path.abspath(cf['b'])
    return config
    
def get_config():
    config = {'daemon':False, 'time':60}
    shortopts = 'p:c:da:b:'
    try:
        optlist, args = getopt.getopt(sys.argv[1:], shortopts)
    except getopt.GetoptError as e:
        print(e)
        print_help()
        sys.exit(1)

    for key, value in optlist:
        if key == '-p':
            config['tdir'] = value
        elif key == '-c':
            config = get_config_fromjson(config, value)
        elif key == '-d':
            config['daemon'] = True
        elif key == '-a':
            if config.has_key('rss'):
                config['rss'].append(value)
            else:
                config['rss'] = [value]
        elif key =='-b':
            config['db'] = os.path.abspath(value)

    check_config(config)

    #remove duplicates
    new_rss = []
    for addr in config['rss']:
        if not addr in new_rss:
            new_rss.append(addr)
    config['rss'] = new_rss

    return config

if __name__ == '__main__':
    print("Begin ut...")
    print("    Test normal arguments...")
    sys.argv = ['asd.py', '-p', '/home', 
                '-a', 'http://hello.com', 
                '-a', 'http://hello.cn',
                '-a', 'http://hello.com',
                '-b', '/home/test.db']
    cfg = get_config()
    assert cfg['tdir'] == '/home'
    assert 'http://hello.com' in cfg['rss']
    assert 'http://hello.cn' in cfg['rss']
    assert len(cfg['rss']) == 2
    assert cfg['daemon'] == False
    assert cfg['db'] == '/home/test.db'

    print("    Test config file...")
    sys.argv = ['asd.py', '-c', 'cfg.json']
    cfg = get_config()
    assert cfg['tdir'] == '/home'
    assert 'http://test1.com' in cfg['rss']
    assert 'http://test2.com' in cfg['rss']
    assert len(cfg['rss']) == 2
    assert cfg['daemon']
    assert cfg['db'] == '/home/test1.db'

    print("    Test cfg1.json...")
    sys.argv = ['asd.py', '-c', 'cfg1.json']
    cfg = get_config()
    assert cfg['tdir'] == '/home'
    assert 'http://test1.com' in cfg['rss']
    assert len(cfg['rss']) == 1
    assert cfg['daemon']
