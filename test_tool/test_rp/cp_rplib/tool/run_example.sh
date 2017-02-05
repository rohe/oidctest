#!/usr/bin/env bash

python3 server.py -p 8080 -f flows -t -k config &> err.log &
