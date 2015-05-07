import os
import sys
import json
from datetime import date
from pprint import pprint
import smtplib
from email.mime.text import MIMEText
from subprocess import call



with open('db.json') as data_file:
    dbConf = json.load(data_file)

#send email function
def sendMail(subject,message):
    with open("mail.json") as data_file:
        mailConf = json.load(data_file)
    s = smtplib.SMTP();
    s.connect(mailConf['host'],mailConf['port']);
    s.starttls();
    s.login(mailConf['email'],mailConf['password']);
    s.sendmail(mailConf['email'],mailConf['to'],message);

today = date.today()
today_str = today.strftime('%Y%m%d')
cmd = "%s -u%s -p%s %s > %s-%s.sql"%(dbConf['bin'],dbConf['user'],dbConf['password'],dbConf['database'],dbConf['database'],today_str);

code = os.system(cmd);
if(code!=0):
    sendMail('database','database export error')
    sys.exit(0)

cmd = 'tar zcvf %s-%s.sql.tar.gz %s-%s.sql'%(dbConf['database'],today_str,dbConf['database'],today_str)

code = os.system(cmd);
cmd = 'rm -rf %s-%s.sql'%(dbConf['database'],today_str)
code = os.system(cmd);



