#!/usr/bin/env bash

NAME="config_server.py"
PORT="60000"

PID=`ps -ax | grep "${NAME}" | grep python | cut -d" " -f2`
if [ -n "${PID}" ] ; then 
  echo "Killing: ${PID}"
  kill -9 ${PID}
  sleep 1
fi

echo -n "Starting ${NAME} ... "
python3 "${NAME}" -k -p "${PORT}" -H html -c tt_config config 2> stderr.log &

if [ $? -eq 0 ] ; then
  echo "OK"
else 
  echo "ERROR"
fi
