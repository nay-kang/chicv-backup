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
    params = {
        "exclude_flash_sale":"0",
        "exclude_activity_promotion":"0"
    };
    start = 0;
    products = [];
    cursor = "open"
    while True:
        params["cursor"] = cursor
        r = requests.get("http://l.stylewe.com/rest/productindex",params=params)
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
        localDir = sys.argv[2]
        products = json.load(jsonFile)
    products_len = len(products)
    for i in range(products_len):
        imageUrl = "image_cache/fill/ffffff/600x600/"+products[i]['images'][0]['image']
        if not os.path.isfile(localDir+imageUrl):
            print("Downloading:("+`(i+1)`+"/"+`products_len`+")"+imageUrl)
            path = os.path.dirname(localDir+imageUrl)
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(localDir+imageUrl))
            urllib.urlretrieve("https://www.stylewe.com/"+imageUrl,localDir+imageUrl)
            time.sleep(2)

context = sys.modules[__name__]
funcName = sys.argv[1];
if funcName in dir(context):
    getattr(context,funcName)()
else:
    print 'function:'+funcName+' not exists!'
