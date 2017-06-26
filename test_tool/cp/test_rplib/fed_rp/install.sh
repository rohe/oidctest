#!/usr/bin/env bash

./setup.py fed_conf_usage https://localhost:8080/sms
./bogus_sms.py fed_conf_usage
