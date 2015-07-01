import json
import smtplib
import os
from email.mime.text import MIMEText

class _util:

	#read json conf
	@staticmethod
	def readConf(path):
		c_dir=os.path.dirname(os.path.abspath(__file__))+"/"
		with open(c_dir+path) as data_file:
			return json.load(data_file)

	#send email function
	@staticmethod
	def sendMail(subject,message):
		mailConf = _util.readConf('mail.json')
		s = smtplib.SMTP();
		s.connect(mailConf['host'],mailConf['port']);
		s.starttls();
		s.login(mailConf['email'],mailConf['password']);
		s.sendmail(mailConf['email'],mailConf['to'],message);

	@staticmethod
	def escapePath(path):
		return path.replace(" ","\\ ")
