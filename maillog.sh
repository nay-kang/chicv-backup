sleep 3
log_content=$(cat "$1")
/usr/bin/python "/data/backup/chicv-backup/main.py" "sendMail" "$2" "$3" ""
cat /dev/null > "$1"

