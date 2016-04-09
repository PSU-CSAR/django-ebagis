def setup(settings_module_name):
    '''get the settings module and add the INSTALLED_APPS and settings
    variables to its scope'''
    from sys import modules
    from .app_settings import EBAGIS_INSTALLED_APPS, EBAGIS_APP_SETTINGS

    # the settings module name is passed in from
    # the outer settings module using __name__
    # note that the inspect module could
    # probably grab the name automatically
    # see https://gist.github.com/techtonik/2151727
    settings = modules[settings_module_name]

    try:
        # append our required apps to the INSTALLED APPS list
        settings.INSTALLED_APPS.append(EBAGIS_INSTALLED_APPS)
    except AttributeError:
        # apparently INSTALLED_APPS is a tuple; concat them
        settings.INSTALLED_APPS += tuple(EBAGIS_INSTALLED_APPS)

    # iterate through the list of vars above and add them to
    # the outer settings module scope
    for key, val in EBAGIS_APP_SETTINGS.iteritems():
        setattr(settings, key, val)
