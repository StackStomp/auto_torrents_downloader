import os
import sys
import getopt
import logging

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

def same_rss_cfg(c1, c2):
    #TODO
    return False

def check_config(config):
    print(config)
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
    if 'tdir' not in config:
        print("Need torrents' directory")
        print_help()
        sys.exit(1)
    if not os.path.isdir(config['tdir']):
        print("The torrents' directory for download is not exists")
        print_help()
        sys.exit(1)
    # test tdirs
    for tdir in config['tdirs']:
        if not os.path.isdir(tdir):
            print("The torrents' directory %s is not exists" % tdir)
            print_help()
            sys.exit(1)
    #-a
    if 'rss' not in config:
        print("No rss feed's address found")
        print_help()
        sys.exit(1)
    for rss in config['rss']:
        if 'address' not in rss:
            print("The rss configuration need an address")
            print(rss)
            sys.exit(1)
        if 'parser' not in rss:
            print("The rss configuration need a parser")
            print(rss)
            sys.exit(1)
        if 'subscriber' in rss:
            if type(rss['subscriber']) != list and \
               type(rss['subscriber']) != str:
               print("Invalid subscriber type(must be e-mail or e-mail list) %s"\
                    % type(rss['subscriber']))
               sys.exit(1)
        if 'filter' in rss:
            for matcher in rss['filter']:
                for kw in matcher.get('key-words', []) \
                        + matcher.get('key-regex', []):
                    if ';' in kw:
                        print("The key words/regex can not contain ';'(%s)" % kw)
                        sys.exit(1)
        for other in config['rss']:
            if id(rss) == id(other):
                break
            if same_rss_cfg(rss, other):
                print("Same rss configuration founded")
                print(other)
                print(rss)
                sys.exit(1)
    #-b
    if 'db' not in config:
        print("No database path specified")
        print_help()
        sys.exit(1)
    #proxy
    if 'proxy' in config:
        if 'type' not in config['proxy']:
            config['proxy']['type'] = 'http'
        if 'host' not in config['proxy']:
            print("There is no 'host' in proxy")
            sys.exit(1)

def get_config_fromjson(config, fdir):
    import json
    with open(fdir,'rb') as f:
        cf = json.load(f)
    config = dict(config, **cf)
    return config
    
def get_config():
    config = {'daemon':None, 
              'time':300, 
              'feedurl-timeout':30,
              'torurl-timeout':60,
              'flush':True,
              'maxtry':10,
              'tdir':'',
              'tdirs':[]}
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
            logging.debug("Begin to read from file {}".format(value))
            config = get_config_fromjson(config, value)
        elif key == '-d':
            config['daemon'] = value
        elif key =='-b':
            config['db'] = os.path.abspath(value)

    if 'ctrl-dir' not in config:
        print("No ctrl-dir specified")
        sys.exit(1)

    config['db'] = os.path.join(config['ctrl-dir'], 'td.db')
    config['log-file'] = os.path.join(config['ctrl-dir'], 'atdownloader.log')
    config['pid-file'] = os.path.join(config['ctrl-dir'], 'atdownloader.pid')

    for i in range(0, len(config['rss'])):
        config['rss'][i]['feedurl-timeout'] = \
            config['rss'][i].get('feedurl-timeout', config['feedurl-timeout'])

    if not config['tdir'] in config['tdirs']:
        config['tdirs'].append(config['tdir'])

    check_config(config)

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
