.. _run_op:

Running the OP test tool
========================

To begin with you will have to manually create description/configuration files
for every OP you want to test.
More about that in the configuration :ref:`config`.

Once you have a configuration file for the OP that should be tested you can
start the test instance by running optest.py::

    usage: optest.py [-h] [-k] [-o OPERATIONS] [-f FLOWS] [-p PROFILE]
                     [-P PROFILES] [-M MAKODIR] [-S STATICDIR] [-s] [-x]
                     [-m PATH2PORT]
                     config

    positional arguments:
      config

    optional arguments:
      -h, --help     show this help message and exit
      -k
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

f/flows
~~~~~~~
Must point to a flows.yaml file which specifies which tests there are and
how they are supposed to act.

k/insecure
~~~~~~~~~~
If the test instance should not try to verify the TLS certificates of the
OP.

.. _path2port:

m/path2port
~~~~~~~~~~~
If the test tool is supposed to work behind a reverse proxy this is the
map between path and port number. It's expected to be a csv file with one
map per line::

    oauth-rp-code-test,8081
    oauth-rp-token-test,8082
    oidc-rp-code-test,8091
    oidc-rp-token-test,8092


M/Makodir
~~~~~~~~~
The directory where Mako is expecting all the files it need to access.
So subdirectories in this directory should be *htdocs*, *modules* and
*template*.

O/Operation
~~~~~~~~~~~
Code that describes what operations the test tool should be able to perform.
This flag should **only** be used if the standard set is not to be used.

.. _run_profile:

p/profile
~~~~~~~~~
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

P/profiles
~~~~~~~~~~
Descriptions of the different flow profiles.
This flag should **only** be used if the standard set is not to be used.

s/tls
~~~~~
Whether the RP should use TLS for all communication. This is not necessary
if the test tool is behind a reverse proxy or other server that
terminates the HTTPS connection before the traffic reaches the test tool.

S/staticdir
~~~~~~~~~~~
If another directory then 'static' should be used for all the static files
then that is specified here.

x/xport
~~~~~~~
Exports the port in the test tool URL. This makes the URL contain both
the path defined by the port-path mapping that the reverse proxy uses and
also the port number. Useful when debugging the test tool.

Usage examples
--------------

The test tool can run in two ways. It can be stand alone, listening on a,
probably non-standard port. Or it can be run behind a `reverse proxy`_ which
then converts a external path to an internal port.

Stand alone
~~~~~~~~~~~

Here the test tool is configured to listen to a specific port.
It can be any port but common is that it's not one of the system ports.
Which is necessary since the test tool normally is not run by root.

If the tool is stand-alone it has to deal with TLS/SSL itself. To do this
the necessary keys and certificates has to be constructed and placed in the
*certs* directory. It is also necessary to use the -s flag to get the
software to do HTTPS. If for some reason there are problems with verifying
the certificates used by the OP, the -k flag kan be use to turn off
certificate verification.

Very simple example where there is a flows.yaml file and a configuration
file named 'config' ::

    optest.py -s -f flows.yaml config


Reverse proxy setup
~~~~~~~~~~~~~~~~~~~

If a reverse proxy is in place then the there will be an external URL
that the RP is known as to the outside but also and internal URL which is
only used between the proxy and the test tool.

An example could be that the external URL would be:
    https://example.com/optest/op1

while the internal URL would be:
    http://localhost:8666/

To accomplish this a couple of things has to happen. If you are running
an Apache server as your reverse proxy you can find a desciption of the
necessary steps on the `apache reverse proxy`_ page.
You probably want to preconfigure a list of path-to-port mappings.
Besides doing this in the reverese proxy you should also construct a csv
file that contains the path2port_ mapping.

If you do that the test tool will construct the correct external URL based
on the *port* specification in the config file and the mapping defined in the
csv file.

Since the reverse proxy will probably be used to terminate the HTTPS
tunnel the tool will not have to deal with certificates which leaves us
with the following simple command::

    optest.py -f flows.yaml -m reverse.csv config


.. _reverse proxy: https://en.wikipedia.org/wiki/Reverse_proxy
.. _apache reverse proxy: http://www.apachetutor.org/admin/reverseproxies
