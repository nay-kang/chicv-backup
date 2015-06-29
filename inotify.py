# AsyncNotifier example from tutorial
#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#
import os
import asyncore
import pyinotify

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE|pyinotify.IN_ISDIR|pyinotify.IN_CREATE  # watched events

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        self.do(event)
    def process_IN_CREATE(self,event):
        self.do(event)
    def process_IN_ISDIR(self,event):
        self.do(event)

    def do(self,event):
	cmd = 'scp %s nay@10.0.2.2:/tmp/upload/%s'%(event.pathname,event.path);
	print cmd
	print event
	if not event.dir:
	    os.system(cmd)
        #print "Creating:", event.pathname

notifier = pyinotify.AsyncNotifier(wm, EventHandler())
wdd = wm.add_watch('/tmp/upload/', mask, rec=True)

asyncore.loop()
