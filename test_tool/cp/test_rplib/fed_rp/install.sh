#!/usr/bin/env bash

./create_bundle.py fed_conf_usage
./create_sms.py fed_conf_usage
./bogus_sms.py fed_conf_usage
