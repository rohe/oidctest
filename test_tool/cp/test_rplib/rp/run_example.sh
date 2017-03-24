#!/usr/bin/env bash

NAME="server.py"
PORT="8080"

PID=`ps -ax | grep "${NAME}" | grep python | cut -d" " -f2`
if [ -n "${PID}" ] ; then 
  echo "Killing: ${PID}"
  kill -9 ${PID}
  sleep 1
fi

echo -n "Starting ${NAME} ... "
python3 "${NAME}" -f flows -p "${PORT}" -k -t conf 2> stderr.log &

if [ $? -eq 0 ] ; then
  echo "OK"
else 
  echo "ERROR"
fi
