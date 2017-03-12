#!/usr/bin/env bash

python3 server.py -f flows -i http://localhost:8080 -p 8080 -t -k -F fed_conf config &
