# Extending the Certification Test Suites

*Version 0.1 - August 11, 2017*

This document describes how to extend the OpenID Connect OP and RP certification environments
that the OpenID Foundation provides with new tests. It lists important directory/file structures
and the steps one would have to take to add a new test to these environments.

### Overview
Test descriptions in JSON format can be found in the following directories.

For the OP test suite:
````
test_tool/cp/test_op/flows
````
For the RP test suite:
````
test_tool/cp/test_rplib/rp/flows
````
To add a test one would create a new file in this directory containing a JSON-formatted description of 
the new test according to the syntax described in the following section.

### JSON Test Description Syntax

###### sequence
Ordered sequence of "behavioral" operations that this test executes.
Values in the sequence are either:
- `string`: operation class
or:
- `object`: operation class + modifier

`docs/appendix_func.md` lists operation classes and methods/modifiers that "sequence" elements can refer to.

###### group
Name of group of tests where this test belongs to.
Use the same string value for tests that you want to combine in a single group.
Only for display in the web UI.

###### desc
Description of the test for display in the web UI.

###### note
Results in an intermediate HTML page displaying a message to the tester; for display in the web UI.

###### usage
- return_type: a list of response types to which this test applies 
- register: use dynamic client registration
- extra: nice to have, not MTI, not should

###### assert
Executed at the end of a test to check the result, and assert state of the test tools is what you expect: 
it determines whether the test passed or not.

###### MTI
Specifies whether a test is mandatory or not; when combined with `usage` `return_type` allows for non MTI tests.

### Optional vs. Mandatory
Tests are grouped in 3 groups

- mandatory : MTI
the "MTI" element is present, possibly restricting the MTI to certain response types by including a list of response types

- should : default

- optional/may : the boolean element "usage"->"extra" is set to true
not that one cannot be granular per response type on should vs. may

### Adding Operations

Behavioral operations that can be referred to by their class name in the `sequence` of a JSON test description.
These are Python classes with a few methods. Most important method is `run`. See `docs/appendix_func.md` for a full
lists of operation classes and methods/modifiers.

Adding operations is done as follows:

##### OP test suite
By adding a class to:
- `src/oidctest/op/oper.py`

and/or a modifier to:
- `src/oidctest/op/func.py`

##### RP test suite
By adding a class to:
- `src/oidctest/rp/operation.py`

and/or a modifier to:
- `src/oidctest/rp/func.py`

### Notes

- test tool stores all events requests/responses
- modifiers/methods are found in `func.py`; context specifies the class that it works on
- sub dictionary is SETUP description, things to be done before running the sequence test element
- set_webfinger_resource will pick URL over acct: and will pick it up if you have set it or skip it if you have not configured webfinger
  in the OP settings
- element in here can be skipped if not configure, e.g. if webfinger is not configured

- One can refer to functions and classes that have been defined in `otest/src/otest/[aus|rp]/func.py` or `oidctest/src/oidctest/[op|rp]/func.py`

- One can also refer to new functions and classes that would have to be added to `/src` first.

- One can refer to "behavior" that has been defined in `otest/src/otest/rp/provider.py` or `oidctest/src/oidctest/[rp|op]/provider.py`
