curl http://172.16.1.14:10003/ptz/config
while true
do
curl http://172.16.1.14:10003/ptz/teacher/set_pos?x=100&y=200
curl http://172.16.1.14:10003/ptz/teacher/get_pos
done
