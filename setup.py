#!/usr/bin/env python
from setuptools import setup, find_packages


PYTHON_REQUIREMENTS = '>=2.7.11,<3.0'


def get_readme():
    with open('README.md', 'r') as r:
        return r.read()


def get_version():
    with open('VERSION.txt', 'r') as v:
        return v.read().strip()


def main():
    readme = get_readme()
    version = get_version()
    download_url = (
        'https://github.com/PSU-CSAR/django-ebagis/tarball/{}'.format(version)
    )

    setup(
        name='django-ebagis',
        #packages=find_packages(),
        py_modules=['manage'],
        version=version,
        description=(
            'Django project implementing the server-side '
            'portion of the PSU CSAR/NWCC BAGIS project.'
        ),
        long_description=readme,
        author=('Portland State University '
                'Center for Spatial Analysis and Research'),
        author_email='jkeifer@pdx.edu',
        url='https://github.com/PSU-CSAR/django-ebagis',
        download_url=download_url,
        entry_points='''
            [console_scripts]
            ebagis=manage:main
        ''',
        python_requires=PYTHON_REQUIREMENTS,
        install_requires=[
            'psycopg2>=2.7.1',
            'celery==3.1.25',
            'django-celery>=3.2.1',
            'Django>=1.10.6',
            'djangorestframework>=3.6.2',
            'GDAL>=2.1.0',
            'drf-chunked-upload>=0.3.0',
            'arcpy-extensions>=0.0.4',
            'djangorestframework-gis>=0.11.0',
            'django-rest-swagger>=2.0.4',
            'django-filter>=1.0.1',
            'django-allauth>=0.31.0',
            'django-redis>=4.3.0',
            'django-split-settings>=0.2.4',
            'pyyaml>=3.12',
            'six>=1.10.0',
            'django-crispy-forms==1.6.1',
        ],
        extras_require={
            'CORS': ['django-cors-headers>=2.0.2'],
            'DEV': [
                'django-extensions>=1.4.9',
                'django-debug-toolbar>=1.7',
                'mock>=2.0.0',
            ],
        },
        dependency_links=[
            'https://github.com/jkeifer/arcpy-extensions/'
            'tarball/master#egg=arcpy-extensions-0.0.4',
        ],
        license='',
    )


if __name__ == '__main__':
    main()
