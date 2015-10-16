sleep 3
log_content=$(cat "$1")
python /media/sf_www/chicv-backup/main.py sendMail "$2" "$3" "$log_content"
cat /dev/null > "$1"

