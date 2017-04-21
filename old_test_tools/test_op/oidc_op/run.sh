#!/usr/bin/env bash

CONF=config.py

if [ -f $CONF ]
then
    :
else
    cp example_conf.py $CONF
fi

optest.py -f flows.yaml -k -p 9100 -m path2port.csv config

