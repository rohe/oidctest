#Set up RP test instance
The test tool for testing an Relying Party is located in the folder:
oidctest/test_tool/test_rp/op 

start the server by runing the command: 
```
python server.py
```

#User interface
In the web user interface the first page could be used to generate static client credentials. The 
second page lists all test which is sorted in to categories.

#Adding new tests
All tests are listed in the static/rp_test_list.js

The structure of the test are the following:
```
[
    ["Headline1", {
        "Test ID 1": {
            "short_description": "",
            "profiles": [PROFILE_1],
            "detailed_description": "",
            "expected_result": ""
        }
    }],
    ["Headline2", {            
        "Test ID 2": {
            "short_description": "",
            "profiles": [PROFILE_2],
            "detailed_description": "",
            "expected_result": ""
        }
    }]
]
```