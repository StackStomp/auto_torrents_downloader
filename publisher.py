# -*- coding: utf-8 -*-  
import os


def publish_event(mail_addr, title, content):
    cmd = '''echo "%s" | mail -v -s ''' % content
    fcmd = '''%s "%s" %s''' % (cmd, title, mail_addr)
    os.system(fcmd)
        
def publish_tordown(mails, tlist):
    '''
Publish the torrents have been downloaded \
to the disk event.'''
    if len(tlist) == 0:
        return

    title = '%d个种子已经开始下载[不要回复]' % len(tlist)
    content = '开始下载的种子文件为：\n'
    for t in tlist:
        content += t
        content += '\n'
    content += '\n此邮件为自动发送，请不要回复'

    for mail in mails:
        publish_event(mail, title, content)


