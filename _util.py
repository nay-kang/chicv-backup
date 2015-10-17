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
	def sendMail(subject,message,to=None):
		mailConf = _util.readConf('mail.json')
		if mailConf['encryption']=='ssl':
			s = smtplib.SMTP_SSL(mailConf['host'],mailConf['port'])
		else :
			s = smtplib.SMTP(mailConf['host'],mailConf['port']);
			s.starttls();

		#s.connect(mailConf['host'],mailConf['port']);
		s.login(mailConf['email'],mailConf['password']);
		msg = MIMEText(message)
		msg['Subject'] = subject
		msg['From'] = mailConf['email']
		if to == None:
			to = mailConf['to']

		msg['To'] = to
		s.sendmail(mailConf['email'],to,msg.as_string());

	@staticmethod
	def escapePath(path):
		return path.replace(" ","\\ ")
