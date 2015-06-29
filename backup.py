import os
import sys
import json
from datetime import datetime
from pprint import pprint
import smtplib
from email.mime.text import MIMEText
from subprocess import call

#generat current data string
today = datetime.now()
today_str = today.strftime('%Y%m%d_%H%M')
#current dir
c_dir=os.path.dirname(os.path.abspath(__file__))+"/"

#send email function
def sendMail(subject,message):
    with open(c_dir+"mail.json") as data_file:
        mailConf = json.load(data_file)
    s = smtplib.SMTP();
    s.connect(mailConf['host'],mailConf['port']);
    s.starttls();
    s.login(mailConf['email'],mailConf['password']);
    s.sendmail(mailConf['email'],mailConf['to'],message);

#backup database
def backupDatabase():
    with open(c_dir+'db.json') as data_file:
        dbConf = json.load(data_file)
    cmd = "%s -u%s -p%s %s > %s-%s.sql"%(dbConf['bin'],dbConf['user'],dbConf['password'],dbConf['database'],dbConf['database'],today_str);
    code = os.system(cmd);
    if(code!=0):
        sendMail('database','database export error')
        return
    cmd = 'tar zcvf %s/%s-%s.sql.tar.gz %s-%s.sql'%(dbConf['backup_path'],dbConf['database'],today_str,dbConf['database'],today_str)
    code = os.system(cmd);
    cmd = 'rm -rf %s-%s.sql'%(dbConf['database'],today_str)
    code = os.system(cmd);

def rsyncFiles():
    with open(c_dir+'file.json') as data_file:
        fileConf = json.load(data_file)
    cmd = 'rsync -vrcz --stats %s %s'%(fileConf['source'],fileConf['dest'])
    code = os.system(cmd)
    if(code!=0):
        sendMail('file rsync','file rsync failed')

def tarFiles():
    with open(c_dir+'file.json') as data_file:
        fileConf = json.load(data_file)
    cmd = 'tar zcvf %s/%s-%s.tar.gz %s'%(fileConf['backup_path'],fileConf['name'],today_str,fileConf['source']);
    code = os.system(cmd)
    if(code!=0):
        sendMail('tar file','tar file failed')
        return

def uploadToS3():
    #TODO
    return

backupDatabase()
rsyncFiles()
#backup files every thuesday
if(today.weekday()==1 and today.hour()==6):
    tarFiles()
