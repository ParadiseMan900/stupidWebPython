gunicorn --bind 127.0.0.1:1234 wsgi:app & APP_PID=$!
sleep 5
echo $APP_PID
kill -TERM $APP_PID
echo process gunicorns kills
exit 0