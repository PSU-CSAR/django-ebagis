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
    packages=['ebagis'],
    version=version,
    description=('Django app implementing the server-side portion of the BAGIS project.'),
    long_description=readme,
    author='Portland State University Center for Spatial Analysis and Research',
    author_email='jkeifer@pdx.edu',
    url='https://github.com/PSU-CSAR/django-ebagis',
    download_url=download_url % version,
    install_requires=[
        'celery>=3.1.17',
        'Django>=1.7.4',
        'django-celery>=3.1.16',
        'djangorestframework>=3.0.1',
        'GDAL>=1.11.2',
        'drf-chunked-upload>=0.1.2',
        'arcpy-extensions>=0.0.2',
        'djangorestframework-gis>=0.8.1',
        'django-rest-swagger>=0.2.9',
    ],
    license='',
)
