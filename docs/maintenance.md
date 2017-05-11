# Operational Maintenance

*Version 1.0 - March 20, 2017*

This document describes operational maintenance procedures for the OpenID Connect OP and RP certification environments
that the OpenID Foundation provides. It lists important directory/file structures and the steps one would have to take
to update the code, documentation and/or configuration of these environments.

For regular maintanance go directly to the [Deployment](#deployment) section.

### SSH Login

Make sure you have an account on the machine that is allowed to execute `sudo` commands. Login to the server with:
````shell
ssh <username>@[op|rp].certification.openid.net
````

### Directories/Files Layout
The directories and files that are important for the OP and RP test environment.

Main source directory:
````
/usr/local/src
````

Dependencies are in the sub directories:
````
fedoidc
otest
oidctest
````

### Installation

NB: not needed on OP/RP machine itself anymore, see:  
[https://github.com/rohe/oidctest/blob/master/INSTALL.md](https://github.com/rohe/oidctest/blob/master/INSTALL.md)

Install:
````
cd /usr/local
oidc_setup /usr/local/src/oidctest oidf
copy/edit config.py and tt_config.py into oidc_op
````

Migrate existing OP test instances:
````
copy entities into oidc_op
copy assigned_ports.json into oidc_op
````

### Certificates
The certificates for the test instances are configured in the configuration files, `config.py` and `conf.py` for the OP and RP respectively
and set to the following paths:
````
SERVER_CERT = "/usr/local/oidf/certs/op.certification.openid.net-Public.crt" 
SERVER_KEY = "/usr/local/oidf/certs/openid.key" 
CERT_CHAIN = "/usr/local/oidf/certs/op.certification.openid.net-Intermediate.crt"
CA_BUNDLE = "/usr/local/oidf/certs/op.certification.openid.net-Intermediate.crt"
````
Note that when these certificates are rolled over, the test instances need to be restarted to pickup the new certs.
The Apache webserver that serves the default landing page on port 443 also points to these certificates so make sure
the names are retained and the apache server is also restarted when the certificates are rolled over with:
````
sudo service apache2 restart
````

### Deployment
These are the actual commands one would give to update the code/configuration and make it available in the production environment.

###### UPDATE
Pulls down source code, needs deploy after that:
````	
cd /usr/local/src
pullall.sh
````

###### DEPLOY
Deploys code into Python packages:
````
cd /usr/local/src
makeall.sh
````

Setup OP and RP instances:
````
cd /usr/local
sudo oidc_setup.py /usr/local/src/oidctest oidf
````

Restart RP test instance:
````
cd /usr/local/oidf/oidc_cp_rplib
./restart.sh
````

Restart OP test instance:
````
cd /usr/local/oidf/oidc_op
sudo ./run.sh
````
NB: the `run.sh` script will also kill the existing OP test instance
