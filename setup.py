#!/usr/bin/env python

import json
from test_ui import version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md', 'r') as r:
    readme = r.read()

download_url = (
    'https://github.com/PSU-CSAR/django-ebagis-ui/tarball/%s'
)


setup(
    name='django-ebagis-test-ui',
    packages=['test_ui'],
    version=version,
    description=('Django app implementing the UI for the server-side portion of the BAGIS project.'),
    long_description=readme,
    author='Portland State University Center for Spatial Analysis and Research',
    author_email='jkeifer@pdx.edu',
    url='https://github.com/PSU-CSAR/django-ebagis-ui',
    download_url=download_url % version,
    install_requires=[
        #'django-ebagis>=0.3.0',
    ],
    license='',
)
