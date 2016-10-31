.. _install:

Quick install guide
###################

For all this to work you need to have Python installed.
The development has been done using 3.5 .
It's made to also work with 2.7 .

Prerequisites
=============

For installing OIDCtest you will need

* otest
* oic
* jwkest

otest
-----
This you have to get from github::

    $ git clone https://github.com/rohe/otest
    $ cd otest
    $ python setup.py install

oic and jwkest
--------------
Both of these should be pulled in from pypi when you install *otest* .
If not you can get them from PyPi::

    $ pip install jwkest
    $ pip install oic

oidctest
--------
Must be gotten from github::

    $ git clone https://github.com/rohe/oidctest
    $ cd oidctest
    $ python setup.py install

Once you have oidctest installed you can construct a new directory from which
to run your test tools.
To do this you can run the script make_test_dir.py like this::

    $ make_test_dir.py <root of the oidctest source tree> <target directory>

When this is completed you will have all the necessary files in the
target directory such that you can change directory to that directory
and then run otest.py . There is a start.sh script and a configuration file
copied into the target directory. You should only have to modify the
configuration file to match your need and then run start.sh. When you have done
this you should be able to connect to the test tool webpage and start your
testing.

Logs from the testtool are kept in several places:

* server_log
    Here you get the test tools internal log in files with the name
    'rp_<port number>.log . So different entities gets separate log files
* log
    This is where the logs that the tester have access to are kept.
    logfiles are stored in a directory tree constructed from issuer id,
    profile and test id. Like this:
    log/https%3A%2F%2Flocalhost%3A8040%2F/C.T.T.T.ns./OP-Response-code

