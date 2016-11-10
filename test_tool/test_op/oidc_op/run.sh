#!/usr/bin/env bash

CONF=conf.py

if [ -f $CONF ]
then
    :
else
    cp example_conf.py $CONF
fi

optest.py -f flows.yaml conf

