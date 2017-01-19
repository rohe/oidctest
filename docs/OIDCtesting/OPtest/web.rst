.. _web interface:


=========================================================================
Running the OP test tool using the form based interface for configuration
=========================================================================

------------------------
The configuration server
------------------------

The configuration server is again a Python script::

    $ config_server.py -h
    usage: config_server.py [-h] [-b BASE_URL] [-c TEST_TOOL_CONF] [-f FLOWDIR]
                            [-m PATH2PORT] [-p PORT] [-t] [-M MAKO_DIR]
                            config

    positional arguments:
      config

    optional arguments:
      -h, --help         show this help message and exit
      -b BASE_URL
      -c TEST_TOOL_CONF
      -f FLOWDIR
      -m PATH2PORT
      -p PORT
      -t
      -M MAKO_DIR


-b
::

You should really set this in the configuration file rather then using
this option. Anyway this is the base from which the tool will construct the
necessary URLs.

-c
::

More about the test tool configuration :ref:`here <tt_config>`

-f
::

The :ref:`flows <tt_opt_flow>` information is passed on to the test tool instance

-m
::

The :ref:`path2port <path2port>` information is passed on to the test tool instance

-p
::

The port the configuration server should listen to

-t
::

Turns on HTTPS support. If set the configuration server will not listen to HTTP
calls only to HTTPS.

-M
::

The :ref:`Mako dir <tt_opt_mako>` information is passed on to the test tool instance

config
::::::

The configuration file looks like this::

    import os

    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    SERVER_CERT = "./certs/cert.pem"
    SERVER_KEY = "./certs/key.pem"
    CERT_CHAIN = None

    #VERIFY_SSL = False

    BASE_URL = 'http://localhost'
    ENT_PATH = './entities'
    ENT_INFO = './entity_info'
    MAKO_DIR = './heart_mako'

    FLOWDIR = './flows'

    PATH2PORT = './path2port.csv'
    PORT_MIN = 9100
    PORT_MAX = 9149


SERVER_CERT, SERVER_KEY and CERT_CHAIN
++++++++++++++++++++++++++++++++++++++

Are only necessary if the test instance is supposed to do HTTPS.

BASE_URL
++++++++

*passed on to the configuration of a test tool instance*
The base from which the urls, that the test instance (as an RP) publishes, are
constructed. This includes claims like *redirect_uris*, *jwks_uri*, *tos_url*,
*logo_uri*, *client_uri*, *policy_uri*, *sector_identifier_uri* and possibly
more.

ENT_PATH
++++++++

*passed on to the configuration of a test tool instance*
A path to where the test configurations are stored. The configurations are
stored in a tree of the form <issuer identifier>/<tag> like this::

    https%3A%2F%2Fexample.com --+-- code
                                |
                                +-- idtoken

As you can see the *issuer identifier* is quoted to be URL safe.
The same goes for the tag though that isn't obvious from the example above.

ENT_INFO
++++++++

*passed on to the configuration of a test tool instance*
This is information about the test instance which is static and
should not differ between different test instances. Some of the information
here represents default values and may be changed.

MAKO_DIR
++++++++

*passed on to the configuration of a test tool instance*
Where the MAKO template files can be found. This is the root directory
so within this directory there must be a ht_docs directory with the
actual templates.

FLOWDIR
+++++++

*passed on to the configuration of a test tool instance*
Directory that contains descriptions of all the tests in a domain specific
manner. One test per file and the information is stored in a JSON format.
If you want to understand more about the test descriptions you can
read more about them in :ref:`Test description language`.

PATH2PORT
+++++++++

*passed on to the configuration of a test tool instance*
More about this :ref:`here <path2port>`.

PORT_MAX, PORT_MIN
++++++++++++++++++

Defines the number of test instances that the configuration server can
spin off and which ports it can use for these. When all ports are taken
no more test instance can be started unless a running test instance is
removed.

-----------------
The web interface
-----------------

When you have started a configuration server you can connect to the
port it listens on and see this:

.. image:: confserv0.png

This page gives you two options, you can either browse the existing
test instance configurations until you find the one you want or you
can go to the page where you can create a new configuration.

Browsing test configurations
::::::::::::::::::::::::::::

What you will see if you chose browsing test instances is something like this:

.. image:: issuerlist.png

Picking one of the issuers, the next page shown will look like this:

.. image:: testinstance.png

Here you can remove a test instance configuration, restart the instance
if it's running or just start it if it's not or change the configuration.
If you change the configuration then the test instance is restarted.

Creating a new configuration
::::::::::::::::::::::::::::

Now, if you go down the configuration way you will get a page like this:

.. image:: testconf0.png

which filled in will look like this:

.. image:: testconf1.png

If you click **submit** you will get the next page where there are some
things you may want to change.

Tool Configuration
::::::::::::::::::

Once you have configured everything to you liking and have clicked
*Save&Start* a test instance will be started with the configuration you
just constructed.

.. image:: verifyconf.png

acr_values
++++++++++

Here you can enter a list of the Authentication Context Class References that
your OP supports.

claims_locales
++++++++++++++

Languages and scripts supported for values in Claims being returned,
represented as a list of BCP47 [`RFC5646`_] language tag values.

enc
+++

Whether the OP support encryption/decryption.

extra
+++++

The test tool contains three sets of tests. Those that are testing something
that is mandatory to support, those that test things that are optional
to support and those that just tests nice to suuport things.
By setting this to **True** you will get the extra set of nice-to-have support
tests.

insecure
++++++++

Even though your server supports HTTPS which it **must** according to the
standard you may use self-signed certificates which can not be verifies.
If that is the case you **MUST** set *insecure* to **True** which will tell the
test instance to not attempt any verification of the certificate.

login_hint
++++++++++

login_hint is something a RP may use as a hint to the Authorization Server
about the login identifier the End-User might use to log in.
Here you can set such a hint using a format that you know your OP will
understand.

profile
+++++++

This is a short-form of the test profile you have set. You can not change
this value since it is constructed from the base values.

sig
+++

Whether the OP supports signing/verifying signatures.

tag
+++

A value you set at the beginning of the configuration to distinguish this
configuration from others you may have. *Can not be changed*

ui_locales
++++++++++

Languages and scripts supported for the user interface, represented as a list
of BCP47 [`RFC5646`_] language tag values.

webfinger_email
+++++++++++++++

If you want to test your OsP support for Webfinger queries you have to supply a
resource specification to use. It can either be a email/acct like string.
Which you would then enter here.

webfinger_url
+++++++++++++

The webfinger resource you want to use is might also be an URL. Which you
would then enter here. If you specify both *webfinger_email* and
*webfinger_url* both will be tested.


.. _RFC5646: http://tools.ietf.org/html/rfc5646

