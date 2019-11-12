# Operational Maintenance

*Version 2.1.1 - November 11, 2019*

This document describes operational maintenance procedures for the OpenID Connect OP and RP certification environments
that the OpenID Foundation provides. It lists important directory/file structures and the steps one would have to take
to update the code, documentation and/or configuration of these environments.

For regular maintenance go directly to the [Deployment](#deployment) section.

### Environments

There are 2 environments, one for production and one for testing. Each environment contains 2 servers, one that runs the OP test
suite and one that runs the RP test suite. All 4 servers are virtual machines running on Amazon EC2 accessible via:
[https://console.aws.amazon.com](https://console.aws.amazon.com).
- OP test suite production server:  
  [op.certification.openid.net](https://op.certification.openid.net:60000)
- RP test suite production server:  
 [`p.certification.openid.net](https://rp.certification.openid.net:8080)
- OP test suite test/development server:  
  [new-op.certification.openid.net](https://new-op.certification.openid.net:60000)
- RP test suite test/development server:  
  [new-rp.certification.openid.net](https://new-rp.certification.openid.net:8080)

### SSH Login

Make sure you have an account on the machine that is allowed to execute `sudo` commands. Login to the server with:

```shell
ssh <username>@[op|rp].certification.openid.net
ssh <username>@[new-op|new-rp].certification.openid.net
```

### Directories/Files Layout
The directories and files that are important for the OP and RP test environment.

Main source directory:

```
/usr/local/src
```

Dependencies are in the sub directories:

```
otest
oidctest
```

There are other dependencies like `pyoidc` and `pyjwkest` that are automatically installed.

### Installation

NB: not needed on OP/RP machine itself anymore.

See also the Docker instructions in the files in the "docker" sub directory for a step-by-step walk-through
for a new installation from scratch. **The docker file is leading for how one deploys a new environment.** It
is also made available for those who want to run a local test suite instance which they can integrate into
their OP/RP development/testing/continuous integration environment.

Install:

```
cd /usr/local
oidc_setup /usr/local/src/oidctest oidf
copy/edit config.py and tt_config.py into oidc_op
```

Migrate existing OP test instances:

```
copy entities into oidc_op
copy assigned_ports.json into oidc_op
```

### Certificates
The certificates for the test instances are configured in the configuration files, `config.py` and `conf.py` for the OP and RP respectively
and set to the following paths:

```
SERVER_CERT = "/usr/local/oidf/certs/op.certification.openid.net-Public.crt" 
SERVER_KEY = "/usr/local/oidf/certs/openid.key" 
CERT_CHAIN = "/usr/local/oidf/certs/op.certification.openid.net-Intermediate.crt"
CA_BUNDLE = "/usr/local/oidf/certs/op.certification.openid.net-Intermediate.crt"
```

Note that when these certificates are rolled over, the test instances need to be restarted to pickup the new certificates.
The Apache web server that serves the default landing page on port 443 also points to these certificates so make sure
the names are retained and the Apache server is also restarted when the certificates are rolled over with:

```
sudo service apache2 restart
```

### Release Management

##### Overview

1. merge/rebase upstream repositories for `rohe/oidctest` and `rohe/otest` into `openid-certification/oidctest` and `openid-certification/otest` respectively
1. possibly also update `openid-certification/oidc-provider-conformance-tests` and `openid-certification/openid-client-conformance-tests` based on upstream changes
1. wait for Travis CI on `oidctest/master` to finish successfully
1. merge `oidctest/master` into `oidctest/stable-release-1.2.x` whilst adapting version numbers and `ChangeLog`
1. deploy on OP/RP production servers according to the steps in the `docker/op_test` and `docker/rp_test` files

##### Notes
- official `oidctest` and `otest` are living in the `openid-certification` organization, upstream repositories are in the `rohe` organization
- pull requests for `oidctest` and `otest` go via their corresponding upstream repositories in the `rohe` organization
- review the commits in the upstream repositories before merging/rebasing to `openid-certification` so we know what to expect
- manage versions of `oidctest`, `otest` and all of its dependencies, most notably `pyoidc`
- aim for releasing only with released and packaged versions of `oidctest`, `otest` and `pyoidc`; as an exception it may be necessary to checkout a specific commit version of `pyoidc`
- branches in `openid-certification/oidctest` are `master`, deployed (as much as needed) on the test environment (`new-op` and `new-rp`) and `stable-release-1.2.x`, (always) deployed on the production environment (`op` and `rp`)
- Docker files in `stable-release-1.2.x` are leading for the installation/deployment process/steps
- `oidctest` version number `1.x.x` relates to a specific OP `2.x.x` version and a specific RP `1.x.x` version and it binds those two together; upgrading OP (or RP respectively) would increase the `oidctest` `1.x.x` version/tag number but not necessarily lead to also a new RP (resp. OP) release
- `otest` releases are managed by git tag in the `openid-certification/otest` repository (i.e. not from upstream)

#### Prerequisites

Local git setup.

##### otest

```
$ cd ~/projects/otest && git remote -v
origin	https://github.com/openid-certification/otest.git (fetch)
origin	https://github.com/openid-certification/otest.git (push)
upstream	https://github.com/rohe/otest.git (fetch)
upstream	https://github.com/rohe/otest.git (push)

$ cd ~/projects/otest && git branch -v
* master 4e06be0 Merge pull request #8 from zmartzone/profile-sig-default-true
```

##### oidc-provider-conformance-tests

```
$ cd ~/projects/oidc-provider-conformance-tests && git remote -v
origin	https://github.com/openid-certification/oidc-provider-conformance-tests.git (fetch)
origin	https://github.com/openid-certification/oidc-provider-conformance-tests.git (push)
upstream	https://github.com/panva/oidc-provider-conformance-tests.git (fetch)
upstream	https://github.com/panva/oidc-provider-conformance-tests.git (push)

$ cd ~/projects/oidc-provider-conformance-tests && git branch -v
* master c450cdb allow for local docker testing
```

##### openid-client-conformance-tests

```
$ cd ~/projects/openid-client-conformance-tests && git remote -v
origin	https://github.com/openid-certification/openid-client-conformance-tests.git (fetch)
origin	https://github.com/openid-certification/openid-client-conformance-tests.git (push)
upstream	https://github.com/panva/openid-client-conformance-tests.git (fetch)
upstream	https://github.com/panva/openid-client-conformance-tests.git (push)

$ cd ~/projects/openid-client-conformance-tests && git branch -v
* master de34004 include response_type checks
```

##### oidctest

```
$ cd ~/projects/oidctest && git remote -v
origin	https://github.com/openid-certification/oidctest.git (fetch)
origin	https://github.com/openid-certification/oidctest.git (push)
upstream	https://github.com/rohe/oidctest.git (fetch)
upstream	https://github.com/rohe/oidctest.git (push)

$ cd ~/projects/oidctest && git branch -v
* master                         557d113 Merge pull request #112 from zmartzone/master
  stable-release-1.2.x           deb2351 release OP 2.3.0 and RP 1.2.0
```

#### Steps

##### otest

```
cd ~/projects/otest
git fetch upstream

git checkout master
git merge upstream/master
git push
```

Possibly release a new `otest` version if changes were applied from upstream via:  
[https://github.com/openid-certification/otest/releases](https://github.com/openid-certification/otest/releases)
Add release notes by looking at the commits since last release.


##### oidc-provider-conformance-tests

```
cd ~/projects/oidc-provider-conformance-tests
git fetch upstream

git checkout master
git rebase upstream/master
git push origin master -f
```

Possibly release a new `oidc-provider-conformance-tests` version if changes were applied from upstream via:  
[https://github.com/openid-certification/oidc-provider-conformance-tests/releases](https://github.com/openid-certification/oidc-provider-conformance-tests/releases)
Add release notes by looking at the commits since last release.


##### openid-client-conformance-tests

```
cd ~/projects/openid-client-conformance-tests
git fetch upstream

git checkout master
git merge upstream/master
git push
```

Possibly release a new `oidc-provider-conformance-tests` version if changes were applied from upstream via:  
[https://github.com/openid-certification/openid-client-conformance-tests/releases](https://github.com/openid-certification/openid-client-conformance-tests/releases)
Add release notes by looking at the commits since last release.


##### oidctest

```
cd ~/projects/oidctest
git fetch upstream

git checkout master
git merge upstream/master
git push
```

###### DO WITH MERGE TOOL - MERGE BUT DON'T COMMIT YET - AND UPDATE VERSION NUMBER, UPDATE CHANGELOG, UPDATE DOCKER FILES

```
git checkout stable-release-1.2.x
git merge master --no-commit

# document changes compared to last release based on the commit history/diff
vi ChangeLog

# if a new version of otest was released, change versions of otest in Docker envs
#  ENV VERSION_OTEST   tags/v0.8.x
vi docker/op_test/Dockerfile
#  ENV VERSION_OTEST   tags/v0.8.x
vi docker/rp_test/Dockerfile

# change versions of oidc-provider-conformance-tests and/or openid-client-conformance-tests
# in the `install:` section of .travis.yml if new versions have been released
#  - cd oidc-provider-conformance-tests
#  - git checkout tags/v2.0.x
# and:
#  - cd openid-client-conformance-tests
#  - git checkout tags/v1.0.x 
vi .travis.yml

# we may also need an update of the OP software node-oidc-provider used in the CI process if a new version was released and it impacts Travis CI, in that case edit:
#   ENV VERSION_NODE_OP   tags/v4.0.x
# in:
vi docker/op/Dockerfile

# if new version of OP suite is required
#  VERSION = '2.3.x'
vi test_tool/cp/test_op/version.py
# if new version of RP suite is required
#  VERSION = '1.2.x'
vi test_tool/cp/test_rplib/rp/version.py


# probably do the release commit with an editor/IDE to record changes in commit message (basically copy the ChangeLog additions):
git commit -m "release OP <2.3.x> and/or RP <1.2.x>" .
git push
```

Tag a new release ON THE STABLE-RELEASE branch!! The tag name is not really that important but it binds together OP and RP versions.

Release a new `oidctest` version via:  
[https://github.com/openid-certification/oidctest/releases](https://github.com/openid-certification/oidctest/releases)
Add release notes by copying the ChangeLog additions.
Again: Tag a new release ON THE STABLE-RELEASE branch!!

##### Publishing Images on Docker Hub
* Checkout the stable release branch
* Run `docker-compose -f docker/docker-compose.yml build` to build images
* Run `docker image list` and determine op_test and rp_test image fingerprints 
* Sign in to docker by running `docker login --username=yourusername`
* Create tags for the newly released version (vX.Y.Z in the following examples) and also the 'latest' tag. 
```
docker tag <op_test_image_fingerprint> openidcertification/op_test:vX.Y.Z
docker tag <op_test_image_fingerprint> openidcertification/op_test:latest
docker tag <rp_test_image_fingerprint> openidcertification/rp_test:vX.Y.Z 
docker tag <rp_test_image_fingerprint> openidcertification/rp_test:latest
```
* Push images to docker hub (don't forget to replace vX.Y.Z with the actual version number before pushing)
```
docker push openidcertification/op_test:vX.Y.Z 
docker push openidcertification/op_test:latest 
docker push openidcertification/rp_test:vX.Y.Z
docker push openidcertification/rp_test:latest 
```
* Verify that the images are listed at https://hub.docker.com/r/openidcertification/op_test/tags and https://hub.docker.com/r/openidcertification/rp_test/tags

### Deployment
These are the actual commands one would give to update the code/configuration and make it available in the production environment.

###### UPDATE
Pulls down source code and deploys after that:

```
cd /usr/local/src/otest
sudo git pull
sudo python3 setup.py install

cd /usr/local/src/oidctest
sudo git pull
sudo python3 setup.py install
```

Note that these commands may result in "You are not currently on a branch" in case specific versions of dependencies are checked out.
That is probably fine.

###### DEPLOY

Setup OP and RP instances:

```
cd /usr/local
sudo oidc_setup.py /usr/local/src/oidctest oidf
```

Restart RP test instance:

```
cd /usr/local/oidf/oidc_cp_rplib
sudo ./run.sh
```
NB: the `run.sh` script will also kill the existing RP test instance

Restart OP test instance:

```
cd /usr/local/oidf/oidc_op
sudo ./run.sh
```
NB: the `run.sh` script will also kill the existing OP test instance
