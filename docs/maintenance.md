# Operational Maintenance

*Version 0.5 - March 2nd, 2017*

This document describes operational maintenance procedures for the OpenID Connect RP certification environment
that the OpenID Foundation provides. It lists important directory/file structures and the steps one would have to take
to update the code, documentation and/or configuration of these environments.

For regular maintanance go directly to the [Deployment](#deployment) section.

### SSH Login

Make sure you have an account on the machine that is allowed to `su` into the `oictest` user. Login to the server with:
````shell
ssh <username>@rp.certification.openid.net
````

Change to the oictest user with the right permissions:
````shell
sudo su oictest
````

### Directories/Files Layout
The directories and files that are important for the OP test environment.

Home directory:
````
/home/oictest
````

Toplevel directory:
````
~/projects
````
Dependencies are in library directories:
````
~/projects/pyjwkest/
~/projects/pyoidc/
````

### Deployment
These are the actual commands one would give to update the code/configuration and make it available in the production environment.

###### INSTALL
NB: not needed on RP machine itself anymore, see:  
[https://github.com/rohe/oidctest/blob/master/INSTALL.md](https://github.com/rohe/oidctest/blob/master/INSTALL.md)

###### UPDATE
Pulls down source code, needs deploy after that:
````	
cd oictest
sudo git pull
<Already up-to-date>
````

###### DEPLOY
Deploys code into Python packages:
````
cd oictest
sudo python3 setup.py install
````

Setup OP instances on 8080 and 8090:
````
cd /home/oictest
oidc_setup.py ~/projects/oidctest/ oidf
oidc_setup.py ~/projects/oidctest/ oidf2
````

Restart OP instance on 8080:
````
cd /home/oictest/oidf/oidc_cp_rplib
ps -aef | grep python
sudo kill 44661
ps -aef | grep python
./run.sh 
ps -aef | grep python
````

Restart OP instance on 8090:
````
cd ../../oidf2/oidc_cp_rplib/
ps -aef | grep python
sudo kill 3241
ps -aef | grep python
./run.sh 
ps -aef | grep python
````
