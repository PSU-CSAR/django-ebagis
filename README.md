django-ebagis-ui
================

This is a django app implementing a user interface for the
ebagis Basin Analysis GIS server-side data management platform.


Installation
------------

Install the development version via pip:

    pip install https://github.com/PSU-CSAR/django-ebagis-ui/zipball/master 

And then add it to your Django `INSTALLED_APPS`:

    INSTALLED_APPS = (
        # ...
        'ebagis_ui',
    )


Note that django-ebagis-ui requires django-ebagis.