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
    download_url=download_url# % version,
    install_requires=[
        amqp>=1.4.6,
        anyjson>=0.3.3,
        billiard>=3.3.0.19,
        celery>=3.1.17,
        Django>=1.7.4,
        django-celery>=3.1.16,
        django-windows-tools>=0.1.1,
        djangorestframework>=3.0.1,
        GDAL>=1.11.2,
        kombu>=3.0.24,
        numpy>=1.9.2,
        pytz>=2014.10,
        drf-chunked-upload>=0.1.2,
        arcpy-extensions>=0.0.1,
        djangorestframework-gis>=0.8.1,
    ],
    dependency_links=[
        'https://github.com/jkeifer/drf-chunked-upload/tarball/0.1.2',
        'https://github.com/jkeifer/arcpy-extensions/tarball/0.0.1',
        'https://github.com/djangonauts/django-rest-framework-gis/tarball/master',
    ],
    license='',
)
