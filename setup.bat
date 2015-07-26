@echo off
Setlocal EnableDelayedExpansion


::
::                    SCRIPT OVERVIEW
::                    ===============
::
:: Use this script to install or update an instance of the
:: django-ebagis-site project. The script will perform all
:: setup task if not already done, including pulling and
:: installing django-ebagis. If run successively, this
:: script will pull updates to ebagis and update the data-
:: base.
::
:: The required arguments for this script are as follows:
::
::   1) instance name -- used for database name et al
::   2) database username -- used to create and access DB
::   3) database password -- same as above
::
:: These three args must be entered into the command line
:: in the same order listed above.
::
::
::                 SCRIPT PREREQUESITES
::                 ====================
::
:: This script requires the following for proper operation:
::
::   - django-ebagis-site django project exists and this
::     script is run within it (this script does not clone
::     its own repo itself)
::   - git is installed and on the system PATH
::   - RabbitMQ is installed (requires Erlang) and
::     rabbitmqctl is on the system PATH (in /sbin)
::   - Anaconda 32-bit is installed and on the system PATH
::   - ArcGIS Desktop is installed (for 32-bit arcpy) and
::     its python is NOT on the system PATH
::   - Geodjango dependencies have been installed; see
::     https://docs.djangoproject.com/en/1.8/ref/contrib/gis/install/
::   - Postgres /bin dir is on the system PATH (see above
::     and also ArcGIS docs regarding compatible PG versions)
::
:: Also note that pulling django-ebagis with write-access
:: requires working SSH authorization for github--HTTPS
:: authentication is not currently supported.
::
::
::                      TODO ITEMS
::                      ==========
::
:: Future refactoring will bring multiple named operations
:: such as install, update, reset, and remove.
::


::--------------------------------------------------------
::                       CONSTANTS
::--------------------------------------------------------

set arc_install_folder="C:\Program Files (x86)\ArcGIS\"


::--------------------------------------------------------
::                      SCRIPT MAIN
::--------------------------------------------------------

pushd %~dp0

call:rabbitmq_setup %1,%3
call:set_env %1
call:get_ebagis
call:install_site_dependencies
call:create_secret_file %1,%2,%3
call:create_database %1,%2,%3

popd

GOTO:EOF


::--------------------------------------------------------
::                       FUNCTIONS
::--------------------------------------------------------

:rabbitmq_setup  -- create RabbitMQ vhost and user for site instance
::               -- %~1: name of vhost/user to create
::               -- %~2: user password
    SETLOCAL
        set name=%~1
        set password=%~2
        set found=False
        REM commented out path, pushd, and popd because added to PATH
        REM set RABBITMQ_SBIN_PATH="C:\Program Files (x86)\RabbitMQ Server\rabbitmq_server-3.4.4\sbin"
        REM pushd %RABBITMQ_SBIN_PATH%
        FOR /F %%i IN ('rabbitmqctl list_vhosts') DO (
            IF %%i==%name% (
        set found=True
            )
        )
        IF %found%==False (
            rabbitmqctl add_vhost %name%
            rabbitmqctl add_user %name% %password%
            rabbitmqctl set_permissions -p %name% %name% ".*" ".*" ".*"
        )
        REM popd
    ENDLOCAL
GOTO:EOF


:set_env     -- activate env, creating env, installing conda packages, and linking arcpy if required
::           -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name% || (
            conda create -n %name% python --file conda-requirements.txt
            call activate %name%
            call:create_arcpy_pthfile
        )
    ENDLOCAL
GOTO:EOF


:create_arcpy_pthfile  -- create the pth file to link anaconda env and arcpy lib
    SETLOCAL
        call:find_anaconda_dir anaconda_path
        call:arcgis_version arc_version_number
        SET arcpy_pth_filename=desktop%arc_version_number%.pth
        SET arcgis_path=%arc_install_folder%Desktop%%arc_version_number%
        SET pthfile=%anaconda_path%\Lib\site-packages\%arcpy_pth_filename%
        @echo %arcgis_path%\bin>%pthfile%
        @echo %arcgis_path%\ArcPy>>%pthfile%
        @echo %arcgis_path%\ArcToolBox\Scripts>>%pthfile%
    ENDLOCAL
GOTO:EOF


:arcgis_version  -- find the major version of arc installed for creating paths to libs
::               -- %~1: return variable for arc version number
    SETLOCAL
        SET min_version=10.1
        SET arcgis_version=""
        pushd %arc_install_folder%
        FOR /d %%i IN (*) DO (
            FOR /f "delims=p tokens=1,2" %%a IN ("%%i") DO (
                IF %%a==Deskto IF %%b GTR %arcgis_version% SET arcgis_version=%%b
            )
        )
        popd
        IF %arcgis_version% LSS %min_version% SET arcgis_version=""
    (ENDLOCAL & REM -- RETURN VALUES
        IF "%~1" NEQ "" SET %~1=%arcgis_version%
    )
GOTO:EOF


:find_anaconda_dir  -- determine path to the anaconda install directory
::                  -- %~1: return variable for dir path
    SETLOCAL
        FOR /F "usebackq tokens=1,2,4" %%i IN (`conda info`) DO (
            IF %%i==default IF %%j==environment set anaconda_path=%%k
        )
    (ENDLOCAL & REM -- RETURN VALUES
        IF "%~1" NEQ "" SET %~1=%anaconda_path%
    )
GOTO:EOF


:get_ebagis  -- pull or clone and install the django-bagis repo
    SETLOCAL
        IF EXISTS ../django-ebagis (
            pushd ../django-ebagis
            git pull
            popd
        ) ELSE (
            git clone git@github.com:PSU-CSAR/django-ebagis.git ../django-ebagis && (
                echo cloned django-ebagis write permissions
                call:install_ebagis
            ) || (
                echo could not clone django-ebagis with write permissions, trying read-only
                git clone https://github.com/PSU-CSAR/django-ebagis.git ../django-ebagis && call:install_ebagis
            )    
        )
    ENDLOCAL
GOTO:EOF


:install_ebagis  -- install django-ebagis to current env in development mode
    pushd ../django-ebagis
    REM pip install -r requirements.txt
    pip install -e .
    popd
GOTO:EOF


:install_site_dependencies
    pip install -r requirements.txt
GOTO:EOF


:create_secret_file -- create the secret file with secret info for django site
::                  -- %~1: name of the project instance
::                  -- %~2: database/rabbitmq user
::                  -- %~3: database/rabbitmq user password                 
    SETLOCAL
        set name=%~1
        set user=%~2
        set pass=%~3
        set secretfile=ebagis_site\secret.py
        REM if the secret file does not exist create it
        if not exist %secretfile% (
            call:create_secret_key secret_key
            @echo SECRET_KEY = '!secret_key!'> %secretfile%
            @echo DATABASE_SETTINGS = {>> %secretfile%
            @echo     'default': {>> %secretfile%
            @echo         'ENGINE': 'django.contrib.gis.db.backends.postgis',>> %secretfile%
            @echo         'NAME': '%name%',>> %secretfile%
            @echo         'USER': '%user%',>> %secretfile%
            @echo         'PASSWORD': '%pass%'>> %secretfile%
            @echo     }>> %secretfile%
            @echo }>> %secretfile%
            @echo BROKER_URL = 'amqp://%name%:%pass%$@localhost:5672/%name%'>> %secretfile%
        )
    ENDLOCAL
GOTO:EOF


:create_secret_key  -- create the secret key for the site secret file
::                  -- %~1: return variable for secret key
    SETLOCAL
        set command='python -c "import random, string; print ''.join([random.SystemRandom().choice('{}{}{}'.format(string.ascii_letters, string.digits, string.punctuation.replace('\'', '').replace('\\', ''))) for i in range(50)])"'
        for /f %%i in (%command%) do set secret_key=%%i
    (ENDLOCAL & REM -- RETURN VALUES
        IF "%~1" NEQ "" SET %~1=%secret_key%
    )
GOTO:EOF


:create_database  -- check for database and create if not present
::                -- %~1: name of the database for which to check/create
::                -- %~2: admin database user to use as owner
::                -- %~3: admin database user password
    SETLOCAL
        set name=%~1
        set user=%~2
        set pass=%~3
        REM first we need to list the local databases and check for an existing one
        set found=False
        FOR /F "usebackq skip=3 tokens=1" %%i IN (`psql -d "user=%user% password=%pass% host=localhost port=5432" -c "\l"`) DO (
            IF %%i==%name% (
                set found=True
            )
        )
        REM if found is false, then we need to create the database
        if %found%==False (
            psql -d "user=%user% password=%pass% host=localhost port=5432" -c "CREATE DATABASE %name% WITH OWNER %user% TEMPLATE postgis_21 TABLESPACE gis_data"
            call:load_database
        )
    ENDLOCAL
GOTO:EOF

:load_database  -- load all site fixtures into the database
    SETLOCAL
        python manage.py makemigrations
        python manage.py migrate
        pushd ebagis_site\fixtures\
        FOR %%i in (*) do python manage.py loaddata %%i
        popd
    ENDLOCAL
GOTO:EOF


:reset_database
  SETLOCAL
    python manage.py flush
    call:load_database
  ENDLOCAL
GOTO:EOF
