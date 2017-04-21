#!/usr/bin/env bash

../../../test_rp/rp/cl/keyserver.sh &
python3 ./cloprp.py -p C.T.T.T.ns. -f flows.yaml conf