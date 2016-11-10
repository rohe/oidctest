Install guidance
----------------

You will need to pick up two packages from github.

- otest, https://github.com/rohe/otest.git

The rest should be found on Pypi

You should do the following:

1. git clone https://github.com/rohe/otest.git
2. cd otest; python setup.py install
3. cd ..
4. git clone https://github.com/rohe/oidctest.git
5. cd oidctest; python setup.py install

You also needs oic and jwkest both of which you can find on pypi.org
They should have been pulled in when you installed oidctest
but if not you must do:

- pip install jwkest
- pip install oic


