django-ebagis-site
==================

This repo contains a django project implementing the
django-ebagis application. Included is a Windows batch
file to simplify setup/installation of this project and
its dependencies on the Basins server.


Installation
------------

The included batch file scripts the configuration process
for this project. It is currently setup specifically for
the Basins server, but I would like to rewrite it to not be
system-specific.

The script assumes Anaconda has been installed to the system
and that the
[GeoDjango dependencies have been installed correctly](https://docs.djangoproject.com/en/1.7/ref/contrib/gis/install/).
The script also assumes the ArcGIS version installed is 10.3;
other versions of ArcGIS will required modification of the script
as some paths are currently hard-coded.

To begin setup, create a project directory with the desired
name and location on disk. Within that directory, clone this
repository. From the command line, navigate to the cloned
directory. Next, run the setup.bat file with three arguments:

    $ setup.bat <name_of_project> <postgres_username> <postgres_password>

The batch file will do the following:

1. Clone the django-ebagis repositry. The script will attempt to use
   a stored ssh key to access the repo with push access, but if that
   fails it will clone the repo read-only over https.

2. Create via conda a python environment for the project using the
   project name, installing the dependencies in `conda-requirements.txt`.

3. Activate said environment.

4. Install django-ebagis via its `requirements.txt`. It will be installed
   in development mode, such that the cloned repo will be linked to the
   environment and changes to its files will effect the project.

5. Install the dependencies in `requirements.txt`, including django-windows-tools.

6. Create a database named with the specified  project name in the
   local postgres installation, using the template `postgis_21`
   and tablespace `gis_data`. The user and password for authentication
   will be those provided to the script as arguments.  
   **NOTE:** the password does not currently get passed
   to the command, so the user must input it again, manually.

7. Create the `secret.py` file required by the settings module,
   containing the project's secret key and the database name,
   user, and password.  
   **NOTE:** this file is not tracked by git and should
   never be added as it contains highly sensitive information.

8. Create a .pth file pointing to arcpy in the environment's
   site-packages folder.

9. Run the `python manage.py migrate` command to setup the database
   to hold the project's models.


Updates
-------

As both this project and the installed django-ebagis are git repositories,
most updates should be easily installed simply by running the `git pull`
command in the root of the repository with updates.


Setting up a Production Instance (e.g., Linking to IIS)
-------------------------------------------------------

The necessary commands to set this up should be mostly
automated through [django-windows-tools](http://django-windows-tools.readthedocs.org/en/latest/quickstart.html).
From the docs:

1. First, cd into the project root directory. Also, 
   ensure the correct conda environment is active.
   If not, use `activate <env_name>` to activate it.

2. Begin by collecting all static assets using the standard
   django manage.py command:
   
      `$ python manage.py collectstatic`

3. Within the `static` directory this command will create, make
   a file called `web.config` with the following:

        <?xml version="1.0" encoding="UTF-8"?>
        <configuration>
          <system.webServer>
            <!-- this configuration overrides the FastCGI handler to let IIS serve the static files -->
            <handlers>
            <clear/>
              <add name="StaticFile" path="*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" />
            </handlers>
          </system.webServer>
        </configuration>

4. Setup the IIS site with the following command:
   
       `$ python manage.py winfcgi_install --site-name <project_name> --monitor-changes-to <full_path_to_touch_this_to_update_cgi.txt> --binding=https://*:443`


Running a Development Instance
------------------------------

A development instance simply requires use of the django
development server and celery. These can easily be started
in separate command prompt windows:

1. First, cd into the project root directory in each window.
   Also, ensure the correct conda environment is active.
   If not, use `activate <env_name>` to activate it.

2. In one window, run the command `python manage.py runserver`.
   This should start the development web server accessible at the
   localhost on port 8000.   
   **NOTE:** do not use this server
   for connections across a network. It is not secure.

3. In the other window, run the command
   `celery -A proj worker -l info`. Celery should start
   running and will then be available for tasks.

Better automation of this process is planned but not a priority.
