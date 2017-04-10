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
        'celery>=3.1.20',
        'Django>=1.10.6',
        'django-celery>=3.1.17',
        'djangorestframework>=3.6.2',
        'GDAL>=2.1.0',
        'drf-chunked-upload>=0.2.2',
        'arcpy-extensions>=0.0.4',
        'djangorestframework-gis>=0.11.0',
        'django-rest-swagger>=2.0.4',
        'django-filter>=1.0.1',
        'django-allauth>=0.31.0',
	'django-redis>=4.3.0',
    ],
    license='',
)
