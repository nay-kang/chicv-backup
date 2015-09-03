import os
import sys
from _util import _util
from datetime import datetime
import socket
import urllib2

#generat current data string
today = datetime.now()
today_str = today.strftime('%Y%m%d_%H%M')

#backup database
def backupDatabase():
    dbConf = _util.readConf('db.json')
    cmd = "%s -u%s -p%s %s > %s-%s.sql"%(dbConf['bin'],dbConf['user'],dbConf['password'],dbConf['database'],dbConf['database'],today_str);
    code = os.system(cmd);
    if(code!=0):
        _util.sendMail('database','database export error')
        return
    cmd = 'tar zcvf %s/%s-%s.sql.tar.gz %s-%s.sql'%(dbConf['backup_path'],dbConf['database'],today_str,dbConf['database'],today_str)
    code = os.system(cmd);
    cmd = 'rm -rf %s-%s.sql'%(dbConf['database'],today_str)
    code = os.system(cmd);
    if(code!=0):
	_util.sendMail('database','database tar error,maybe out of space')

#rsync all image files
def rsyncFiles():
    fileConf = _util.readConf('remote_sync.json')
    cmd = 'rsync -vrczL --delete --stats --chmod=a+rwx --perms %s %s'%(fileConf['local'],fileConf['remote'])
    code = os.system(cmd)
    if(code!=0):
        _util.sendMail('file rsync','file rsync failed')

#archvie all image files
def tarFiles():
    fileConf = _util.readConf('file.json')
    cmd = 'tar zcvfh %s/%s-%s.tar.gz %s'%(fileConf['backup_path'],fileConf['name'],today_str,fileConf['source']);
    code = os.system(cmd)
    if(code!=0):
        _util.sendMail('tar file','tar file failed')
        return

def simpleWebTest():
    socket.setdefaulttimeout(15)
    if(len(sys.argv)<3):
        print 'there is no url in argv';
    url = sys.argv[2]
    req = urllib2.Request(url)
    isPass = False
    emailContent = 'url is :'+url
    #emailContent = 'url test failed';
    try:
        response = urllib2.urlopen(req)
        body = response.read()
        if(body.find('<!DOCTYPE html>')==0):
            print 'test ok',today
            isPass = True
        else:
            isPass = False
            emailContent += 'status is 200,but content is not right\n'+body;
    except urllib2.HTTPError as e:
        print e.code
        #print e.read()
        emailContent += 'status code:'+str(e.code)+'\n'+e.read()
    if(not isPass):
        _util.sendMail('web test failed',emailContent)

def uploadToS3():
    #TODO
    print "go S3"
    return

context = sys.modules[__name__]
funcName = sys.argv[1];
if funcName in dir(context):
    getattr(context,funcName)()
else:
    print 'function:'+funcName+' not exists!'
