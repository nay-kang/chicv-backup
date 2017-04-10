# -*- coding: utf-8 -*-
import os
import sys
from _util import _util
from datetime import datetime
import socket
import urllib2
import re
import requests
import json
import urllib
import time
import urlparse
import threading
import thread


#generat current data string
today = datetime.now()
today_str = today.strftime('%Y%m%d_%H%M')

#backup database
def backupDatabase():
    dbConf = _util.readConf('db.json')
    cmd = "%s -u%s -p%s -h%s %s --skip-lock-tables > %s-%s.sql"%(dbConf['bin'],dbConf['user'],dbConf['password'],dbConf['host'],dbConf['database'],dbConf['database'],today_str);
    print cmd
    code = os.system(cmd);
    print 'code',code
    if(code!=0):
        _util.sendMail('database','database export error')
        return
    cmd = 'tar zcvf %s/%s-%s.sql.tar.gz %s-%s.sql'%(dbConf['backup_path'],dbConf['database'],today_str,dbConf['database'],today_str)
    code = os.system(cmd);
    cmd = 'rm -rf %s-%s.sql'%(dbConf['database'],today_str)
    code = os.system(cmd);
    if(code!=0):
        _util.sendMail('database','database tar error,maybe out of space')
    clearBackupDBHistory()

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

def clearBackupDBHistory():
    dbConf = _util.readConf('db.json')
    files = os.listdir(dbConf['backup_path'])
    files.sort()
    remainFiles = dict()
    deleteFiles = []
    p = re.compile('^stylewe-(\d{8}).*\.sql');

    for i in range(len(files)):
        m = p.match(files[i])

        # not a regular auto backup file
        if not m:
            continue

        backDate = m.group(1)
        backDate = datetime.strptime(backDate,'%Y%m%d');

        # if backup time in 30 days don't delete
        if (today-backDate).days < dbConf['remain_days']:
            continue

        yearWeek = `backDate.isocalendar()[0]`+'_'+`backDate.isocalendar()[1]`

        if remainFiles.has_key(yearWeek):
            print 'delete:',files[i]
            cmd = 'rm -rf '+dbConf['backup_path']+files[i]
            print cmd
            os.system(cmd)
        else:
            remainFiles[yearWeek] = True
            print 'remain:',files[i]


def uploadToS3():
    #TODO
    print "go S3"
    return

def sendMail():
    content = ''
    if len(sys.argv) >= 5:
        content = sys.argv[4]
    else:
        stdin = sys.stdin.readlines()
        for i in range(len(stdin)):
            content = content+stdin[i]

    _util.sendMail(sys.argv[3],content,sys.argv[2])

def dumpAllProducts():
    domain = sys.argv[2];
    params = {
        "exclude_flash_sale":"0",
        "exclude_activity_promotion":"0",
        "sorts":"-point"
    };
    start = 0;
    products = [];
    cursor = "open"
    while True:
        params["cursor"] = cursor
        r = requests.get(domain+"/rest/productindex",params=params,verify=False,headers={'Accept-Encoding':'deflate, gzip'})
        products+=r.json()["list"]
        print(len(r.json()["list"]))
        if len(r.json()["list"])==0:
            break
        cursor = r.json()['cursor']

    with open('products.json','w') as jsonFile:
        json.dump(products,jsonFile)

    print(len(products))

def downProductPics():
    with open('products.json','r') as jsonFile:
        products = json.load(jsonFile)

    localDir = sys.argv[2]
    domain = sys.argv[3]
    image_params = sys.argv[4]
    image_index = sys.argv[5]
    products_len = len(products)
    for i in range(products_len):
        max_image_index = min(len(products[i]['images']),image_index)

        for j in range(max_image_index):
            imageUrl = u"/image_cache/"+image_params+products[i]['images'][j]['image']
            print("Downloading:("+`(i+1)`+":"+j+"/"+`products_len`+")"+imageUrl)
            downFileThread(domain,imageUrl,localDir)


def downFileThread(domain,url,localDir):
    print threading.activeCount()
    while True:
        if threading.activeCount()>5:
            time.sleep(1)
        else:
            t = threading.Thread(target=downFile,args=(domain,url,localDir,))
            t.start()
            return True


def downFile(domain,url,localDir):
    if not os.path.isfile(localDir+url):
        print("Downloading:"+url)
        d_file = localDir+url
        path = os.path.dirname(d_file)

        if not os.path.exists(path):
            os.makedirs(path)
        try:
            urllib.urlretrieve(domain+iriToUri(url),d_file)
        except:
            print sys.exc_info()

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

context = sys.modules[__name__]
funcName = sys.argv[1];
if funcName in dir(context):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    getattr(context,funcName)()
else:
    print 'function:'+funcName+' not exists!'
