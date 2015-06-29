#!/bin/bash

if ! pgrep -f 'remote_sync.py' > /dev/null
then
	pwd=$(dirname $0)
	/usr/bin/python "$pwd/remote_sync.py"
fi
