To begin with we will have to manually create description/configuration files for every tester.

The conf_op2.py file can be used as a pattern.

Once you have a configuration file for the OP that should be tested you can start the
test instance by running:

python3 optest.py -p C.T.T.T.ns. -f flows.yaml <config file>

The string 'C.T.T.T.ns' is a description of what the OP says it can handle.

The interpretation is as follows:

C = Flow (C=Code, I=Implicit, D=Direct Access)
T = Can do Webfinger (T=True, F=False)
T = Dynamic Provider Configuration discovery (T=True, F=False)
T = Dynamic Client registration (T=True, F=False)
ns = refers to crypto/JWT capabilities (n=unsigned, s=signed, e=encrypted)

So 'I.T.F' means: 
Can do Implicit flow and dynamic provider discovery but not dynamic client
registration nor any crypto.

usage: optest.py [-h] [-o OPERATIONS] [-f FLOWS] [-p PROFILE] [-P PROFILES]
                 [-M MAKODIR] [-S STATICDIR] [-s]
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

For the time being the only arguments that should be used is -p and -f .
Since the test instance is not supposed to do SSL/TLS then -s is out of the question.
And the other arguments are place holders for further development. 