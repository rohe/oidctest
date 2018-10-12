#!/usr/bin/env bash

conf_file=$( openssl version -a | awk '$1~/^OPENSSLDIR/{gsub(/"/,"",$2);print $2"/openssl.cnf"}' )
openssl req -x509 -newkey rsa:4096 -keyout key.pem -nodes -out cert.pem -days 365 \
  -extensions SAN \
  -subj "/CN=${1:?usage: $0 hostname}" \
  -config  <(cat $conf_file; printf "\n[SAN]\nsubjectAltName=DNS:$1")
