#!/bin/bash

if ! pgrep -f 'remote_sync.py' > /dev/null
then
	echo 'start remote_sync'
	pwd=$(dirname $0)
	/usr/bin/python "$pwd/remote_sync.py" 2>&1
fi
