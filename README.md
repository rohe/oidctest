[![Build Status](https://travis-ci.org/openid-certification/oidctest.svg?branch=master)](https://travis-ci.org/openid-certification/oidctest)

OIDC test tool
==============

OIDCtest is a set of tools for testing OIDC implementations.

The OpenID Foundation (OIDF) provides an OpenID Connect self-certification service on top of this
suite, see: http://openid.net/certification/

Docker
------
Whilst official self-certification happens at the service provided by the OIDF you can locally
spin up the same services to test your OpenID Connect implementation using Docker as described below.
````
docker-compose -f docker/docker-compose.yml up
````
that will run the OP and RP test suite and an actual OP in a docker-compose setting.
Then add the following entries to your `/etc/hosts` file:
````
127.0.0.1 op_test op rp_test
````
You can then access [https://op_test:60000](https://op_test:60000) for OP testing in the same way as you'd go to https://op.certification.openid.net:60000 

Alternatively you can use [https://rp_test:8080](https://rp_test:8080) for RP testing in the same way as you'd use https://rp.certification.openid.net:8080
i.e. by pointing your RP Client to the issuer `https://rp_test:8080/<rp_id>` using Dynamic Client Registration.
