In order to run the make_desc.py script you need to have
oidctest and otest installed.
You MUST get them from github, preferably from
https://github.com/rohe/oidctest and https://github.com/rohe/otest respectively.

There are 3 variables in the script you must keep accurate:

This you should not have to change
REPO = "https://github.com/rohe"

These you must change everytime either the otest or oidctest repos are
updated.

OTEST_BLOB = "1304cd0c079811c96a95eceeeee8bafc7a8a01ee"
OIDCTEST_BLOB = "bcf4457c5920414b0a619d3e34a9262ffe214dc8"

Actually you only have to do it every time one of these files are
changed:

- otest/check.py
- otest/aus/check.py
- otest/func.py
- oidctest/op/check.py
- oidctest/op/func.py

These are commit identifiers and are vital to get the links into the code
correct.

They way to get them are to used 'git'. More specifically you can do:

git log | head -n 1

which will give you a line like this

commit 26c562e9bd79de5a610b613e1093012ba7e1daa8

The value is the commit identifier.

If you have done all of this correctly, then you should only have to do:

./make_desc.py > test_desc.html

in the directory where the make_desc.py file resides.
