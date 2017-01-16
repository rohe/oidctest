.. _op_view:

An overview of the OP test tool
===============================

A basic assumption for the tool is that when you want to test an OpenID
Connect Provider (OP) you may want test one specific aspect at a time.
You may therefor want to have several configurations per OP.
It is for instance common to have one configuration per response_type.
Following on that you will run one test instance per configuration.

How to configure a test instance
--------------------------------

There are 2 basic ways of configuring a test instance, either you use the
web interface provided or you can instead be content with using the RESTish
interface.

* How to configure a test instance using the :ref:`web interface`
* How to configure a test instance using the :ref:`rest interface`

Once you have configured a test instance, using the test instance doesn't
differ depending on how you have configured it.

Running a test instance
-----------------------

To run a test instance you have to use a Python script 'optest.py' which is part
of the oidctest distribution.

There are a number of arguments the script takes and I will go through
them below one by one.

This is the overall pattern::

    $ optest.py -h
    usage: optest.py [-h] [-k] [-i ISSUER] [-f FLOWS] [-p PORT] [-M MAKODIR]
                     [-S STATICDIR] [-s] [-t TAG] [-m PATH2PORT]
                     config

    positional arguments:
      config

    optional arguments:
      -h, --help    show this help message and exit
      -k            insecure mode for when you're expecting to talk HTTPS to
                    servers that use self-signed certificates
      -i ISSUER     The issuer ID of the OP
      -f FLOWS      A file that contains the flow definitions for all the tests
      -p PORT       Which port the server should listen on
      -M MAKODIR    Root directory for the MAKO template files
      -S STATICDIR  Directory where static files are kept
      -s            Whether the server should support incoming HTTPS
      -t TAG        An identifier used to distinguish between different
                    configuration for the same OP instance
      -m PATH2PORT  CSV file containing the path-to-port mapping that the reverse
                    proxy (if used) is using

-h/--help
:::::::::

Will print the usage description as shown above

-k
::

If nothing else is said the tool will try to verify the certificates used
in the HTTPS connection. This will not work if the OP uses self-signed
certificates. Hence, the *-f* flag will turn of certification verification.

-i
::

The Issuer identifier of the OP that is to be tested.

-f
::

.. _tt_opt_flow:

A YAML file that contains descriptions of all the tests in a domain specific
manner. If you want to understand more about the test descriptions you can
read more about them in :ref:`Test description language`.

-p
::

Which port the test instance should listen on. Each test instance **MUST**
have its own port.

-M
::

.. _tt_opt_mako:

Mako is used as the bases for the WEB UI. If nothing is specified the
directories that contains the MAKO templates ('htdocs', 'modules', ...) are expected
to be in the directory from which optest.py is run. If that is not the
case you have to give the path to the root here.

-S
::

There are a bunch of static files that the tool must be able to access.
These are all the javascirpt files, the png, gif and css files. If nothing
is specified they are expected to be in a directory named 'static' in the
directory from which optest.py is run.

-s
::

If the test instance should use HTTPS then set this flag. If so the
configuration file must contain specifications of there the certificate and
key files are.

-t
::

If you have several configurations for one and the same OP then you can
set a name each one of them, this is the *tag*.

-m
::

.. _path2port:


If you are running the test instance behind a reverse proxy you will
want to translate between a path specification on the external side
of the proxy and a port on the inside.

If for instance the test tool runs on optest.example.com then the publicly
available path may be https://optest.example.com/test-00 which then by the
reverse proxy would be translated into for instance http://localhost:8090.
Given that the test instance was listening on port 8090.

The file that the *-m* flag points to is a csv file with two columns,
the first contains the externally visible path and the second contains the
internal port::

    Path,Port
    test-00,8090
    test-01,8091
    test-02,8092

and so on.

config
::::::

.. _tt_config:

The configuration file looks like this::

    import os

    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    SERVER_CERT = "certs/cert.pem"
    SERVER_KEY = "certs/key.pem"
    CERT_CHAIN = None

    # VERIFY_SSL = False

    BASE = 'http://localhost'
    ENT_PATH = 'entities'
    ENT_INFO = 'entity_info'

    KEYS = [
        {"key": "keys/enc.key", "type": "RSA", "use": ["enc"]},
        {"key": "keys/sig.key", "type": "RSA", "use": ["sig"]},
        {"crv": "P-256", "type": "EC", "use": ["sig"]},
        {"crv": "P-256", "type": "EC", "use": ["enc"]}
    ]


This configuration file is most probably the same for every test instance.
The configuration in the entity_info is part of it the same for every instance
the other part is default values for some parameters. What is in the
entities directory is not the same for two test instances.

SERVER_CERT, SERVER_KEY and CERT_CHAIN
______________________________________

Are only necessary if the test instance is supposed to do HTTPS.

BASE
____

The base from which the urls, that the test instance (as an RP) publishes, are
constructed. This includes claims like *redirect_uris*, *jwks_uri*, *tos_url*,
*logo_uri*, *client_uri*, *policy_uri*, *sector_identifier_uri* and possibly
more.

ENT_PATH
________

A path to where the test configurations are stored. The configurations are
stored in a tree of the form <issuer identifier>/<tag> like this::

    https%3A%2F%2Fexample.com --+-- code
                                |
                                +-- idtoken

As you can see the *issuer identifier* is quoted to be URL safe.
The same goes for the tag though that isn't obvious from the example above.

ENT_INFO
________

This is information about the test instance which is static and
should not differ between different test instances. Some of the information
here represents default values and may be changed.

KEYS
____

The test instance needs a set of key for signing and encryption. This is
where the set of keys are defined. The configuration sample above
specifies 4 keys, two RSA keys and 2 elliptic curve keys. For each type one
for signing and one for encryption purposes.

Usage examples
--------------

The test tool can run in two ways. It can be stand alone, listening on a,
probably non-standard port. Or it can be run behind a `reverse proxy`_ which
then converts a external path to an internal port.

Stand alone
:::::::::::

Here the test tool is configured to listen to a specific port.
It can be any port but common is that it's not one of the system ports.
Which is necessary since the test tool normally is not run by root.

If the tool is stand-alone it has to deal with TLS/SSL itself. To do this
the necessary keys and certificates has to be constructed and placed in the
*certs* directory. It is also necessary to use the -s flag to get the
software to do HTTPS. If for some reason there are problems with verifying
the certificates used by the OP, the -k flag kan be use to turn off
certificate verification.

Very simple command example where there is a flows.yaml file and a configuration
file named 'config' ::

    optest.py -p 8091 -i https://example.com/op -t default -s -f flows.yaml config


Reverse proxy setup
:::::::::::::::::::

If a reverse proxy is used then the there will be an external URL
that the RP is known as to the outside but also and internal URL which is
only used between the proxy and the test tool.

An example could be that the external URL is:
    https://example.com/optest/op1

while the internal URL is:
    http://localhost:8666/

To accomplish this a couple of things has to happen. If you are running
an Apache server as your reverse proxy you can find a description of the
necessary steps on the `apache reverse proxy`_ page.
You probably want to pre-configure a list of path-to-port mappings.
Besides doing this in the reverese proxy you should also construct a csv
file that contains the `path2port`_ mapping.

If you do that, the test tool will construct the correct external URL based
on the *port* specification and the mapping defined in the
csv file.

Since the reverse proxy will probably be used to terminate the HTTPS
tunnel the tool will not have to deal with certificates which leaves us
with the following simple command::

    optest.py -p 8092 -i https://example.com/op -t default -f flows.yaml -m reverse.csv config


.. _reverse proxy: https://en.wikipedia.org/wiki/Reverse_proxy
.. _apache reverse proxy: http://www.apachetutor.org/admin/reverseproxies
