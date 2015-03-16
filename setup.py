#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('VERSION.txt', 'r') as v:
    version = v.read().strip()

with open('README.md', 'r') as r:
    readme = r.read()

download_url = (
    'https://github.com/PSU-CSAR/django-ebagis/tarball/%s'
)


setup(
    name='django-ebagis',
    packages=['django-ebagis'],
    version=version,
    description=('Django app implementing the server-side portion of the BAGIS project.'),
    long_description=readme,
    author='Portland State University Center for Spatial Analysis and Research',
    author_email='jduh@pdx.edu',
    url='https://github.com/PSU-CSAR/django-ebagis',
    download_url=download_url % version,
    install_requires=[],
    license=''
)
