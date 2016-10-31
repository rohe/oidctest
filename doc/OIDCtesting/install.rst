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
