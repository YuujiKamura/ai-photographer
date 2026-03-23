#!/bin/bash
mkdir -p /home/user/camera_tmp
for i in $(seq 1 18); do
  ts=$(date +%Y%m%d_%H%M%S)
  curl -s --connect-timeout 10 --max-time 15 http://192.0.0.4:8080/photo.jpg -o "/home/user/camera_tmp/${ts}.jpg"
  python3 /home/user/rotate.py "/home/user/camera_tmp/${ts}.jpg"
  echo "[$i/18] ${ts}.jpg captured"
  [ $i -lt 18 ] && sleep 10
done
echo "DONE"