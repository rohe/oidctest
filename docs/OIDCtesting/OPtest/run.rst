.. _run_op:

Running the OP test tool
========================

To begin with you will have to manually create description/configuration files
for every OP you want to test.
More about that in the configuration :ref:`config`.

Once you have a configuration file for the OP that should be tested you can
start the test instance by running optest.py::

    usage: optest.py [-h] [-o OPERATIONS] [-f FLOWS] [-p PROFILE] [-P PROFILES]
                     [-M MAKODIR] [-S STATICDIR] [-s] [-x] [-m PATH2PORT]
                     config

    positional arguments:
      config

    optional arguments:
      -h, --help     show this help message and exit
      -o OPERATIONS
      -f FLOWS
      -p PROFILE
      -P PROFILES
      -M MAKODIR
      -S STATICDIR
      -s
      -x             ONLY for testing
      -m PATH2PORT

Arguments
---------

profile
~~~~~~~
If profile is not specified it is taken from the configuration file.
The format of the profile string is as follows:

* Flow (C='code', I='id_token', T='token', CI='code id_token',
  IT='idtoken token', CIT='code id_token token')
* Do Webfinger (T=True, F=False)
* Do Dynamic Provider Configuration discovery (T=True, F=False)
* Do Dynamic Client registration (T=True, F=False)
* refers to crypto/JWT capabilities (n=unsigned, s=signed, e=encrypted)

So 'C.T.T.F' means:
Do Code flow use WebFinger and dynamic provider discovery but not dynamic client
registration nor any crypto.

flows
~~~~~
Must point to a flows.yaml file which specifies which tests there are and
how they are supposed to act.

x/insecure
~~~~~~~~~~
If the test instance should not try to verify the TLS certificates of the
OP.

path2port
~~~~~~~~~
If the test tool is supposed to work behind a reverse proxy this is the
map between path and port number. It's expected to be a csv file with one
map per line::

    oauth-rp-code-test,8081
    oauth-rp-token-test,8082
    oidc-rp-code-test,8091
    oidc-rp-token-test,8092


s/tls
~~~~~
Whether the RP should use TLS for all communication. This is not necessary
if the test tool is behind a reverse proxy or other functions that
terminates the HTTPS connection before the traffix reaches the test tool.

S/staticdir
~~~~~~~~~~~
If another directory then 'static' should be used for all the static files
then that is specified here.

M/Makodir
~~~~~~~~~
The directory where Mako is expecting all the files it need to access.
So subdirectories in this directory should be *htdocs*, *modules* and
*template*.

O/Operation
~~~~~~~~~~~
Code that describes what operations the test tool should be able to perform.
This flag should **only** be used if the standard set is not to be used.

P/profiles
~~~~~~~~~~
Descriptions of the different flow profiles.
This flag should **only** be used if the standard set is not to be used.

Command example
---------------

Very simple example where there is one flows.yaml file and a configuration
file named 'config' ::

    python3 optest.py -f flows.yaml -s config


Slightly more complex. This test instance is behind a reverse proxy so
it doesn't need to run HTTPS. It also will have a base URL that doesn't contain
the port number but instead a path description. And Lastly you want to use a
profile that is not the default profile specified in the config file ::

    python3 optest.py -f flows.yaml -m reverse.csv -p C.T.T.T.nse config


