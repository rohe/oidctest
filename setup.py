#!/usr/bin/python
#
# Copyright (C) 2015 Umea Universitet, Sweden
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from setuptools import setup, find_packages

__author__ = 'rohe0002'

setup(
    name="oidctest",
    version="0.5.0",
    description="Test framework for testing OpenID Connect provider and "
                "relaying party implementations",
    author="Roland Hedberg",
    author_email="roland.hedberg@umu.se",
    license="Apache 2.0",
    packages=find_packages('src'),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    install_requires=[
        "argparse",
        "requests >= 2.0.0",
        'future',
        'CherryPy',
        'oic >= 0.9.1',
        'otest'
    ],
    zip_safe=False,
    scripts=['script/optest.py', 'script/make_test_dir.py']
)
