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


Setup
-----

Once you have oidctest installed you can construct a new directory from which
to run your test tools.
To do this you can run the script make_test_dir.py like this::

    $ oidc_setup.py <root of the oidctest source tree> <target directory>

for me this turned out to be::

    $ oidc_setup.py /Users/roland/code/oidctest oidf

.. Note:: that the root of the source tree specification must be absolute.

This will build a file tree in 'oidf' that will loook like this::

    oidf --+-- oidc_op
           |
           +-- oidc_rpinst
           |
           +-- oidc_rplib

Dependent on whether you want to run OP, RP instance or RP library tests
one or the other of these library will be of more interest to you.

How you use the different tools are described here:

:oidc_op:
    :ref:`op`
:oidc_rpinst:
    :ref:`rpinst`
:oidc_rplib:
    :ref:`rplib`

