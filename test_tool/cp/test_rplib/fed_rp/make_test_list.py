import json

from oidctest.fed.test_list import get_mandatory
from oidctest.fed.test_list import test_list

file_dir = 'flows'

fp = open('links.json', 'r')
links = json.load(fp)
fp.close()

grps = [
    "Single SMS", "Multiple SMS", "Policy Breach", "Wrong Signing Key"
]
mandatory = get_mandatory(file_dir, links)
print("\n".join(test_list(mandatory, grps)))
