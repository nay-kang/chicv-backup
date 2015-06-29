import os
import asyncore
import pyinotify
import re
from _util import _util

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE|pyinotify.IN_ISDIR|pyinotify.IN_CREATE  # watched events

conf = _util.readConf('remote_sync.json');

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CLOSE_WRITE(self, event):
		self.do(event)
	def process_IN_CREATE(self,event):
		self.do(event)
	def process_IN_ISDIR(self,event):
		self.do(event)

	def do(self,event):
		remote_path = event.pathname.replace(conf['local'],'');
		if event.dir:
			remote_path = re.sub(r'\/.*$','','/'+remote_path)
		cmd = 'scp -r %s %s/%s'%(event.pathname,conf['remote'],remote_path);

		print event
		if not (not event.dir and event.maskname == 'IN_CREATE'):
			print cmd
			os.system(cmd)

notifier = pyinotify.AsyncNotifier(wm, EventHandler())
wdd = wm.add_watch(conf['local'], mask, rec=True)

asyncore.loop()
