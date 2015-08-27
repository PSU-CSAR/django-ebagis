@echo off
Setlocal EnableDelayedExpansion


:: ---------------------------------------------------------------------------
::
:: ebagis.bat -- commands for ebagis administration
:: Authored July 26, 2015 by Jarrett Keifer
::
:: To see how to use this script, please run it from the command line like so:
:: ebagis.bat help
::
:: ---------------------------------------------------------------------------

GOTO :BEGIN

::--------------------------------------------------------
::                     HELP MESSAGES
::--------------------------------------------------------

:show_info
echo.
echo - TOOL OVERVIEW -
echo.
echo This tool provides administrative operations for ebagis.
echo.
echo.
echo - TOOL PREREQUESITES -
echo.
echo This tool requires the following for proper operation:
echo.
echo   - django-ebagis-site django project exists and this
echo     script is run within it (this script does not clone
echo     its own repo itself)
echo   - git is installed and on the system PATH
echo   - RabbitMQ is installed (requires Erlang) and
echo     rabbitmqctl is on the system PATH (in /sbin)
echo   - Anaconda 32-bit is installed and on the system PATH
echo   - ArcGIS Desktop is installed (for 32-bit arcpy) and
echo     its python is NOT on the system PATH
echo   - Geodjango dependencies have been installed; see
echo     https://docs.djangoproject.com/en/1.8/ref/contrib/gis/install/
echo   - Postgres /bin dir is on the system PATH (see above
echo     and also ArcGIS docs regarding compatible PG versions)
GOTO:EOF


:show_commands
echo Available commands:
echo -------------------
echo.
echo ebagis.bat help -- show full help message
echo ebagis.bat install -- run the installation steps to setup an ebagis instance
echo ebagis.bat upgrade -- pull updates to dependencies and upgrade the database schema
echo ebagis.bat reset -- re-initialize the project instance
echo ebagis.bat remove -- reverse the installation steps and completely remove all dependencies
echo.
echo All of these commands also have specific help messages.
GOTO:EOF


:show_help_install
echo.
echo Use this script to install or update an instance of the
echo django-ebagis-site project. The script will perform all
echo setup tasks if not already done, including pulling and
echo installing django-ebagis. Adding the optional argument
echo --IIS will link this instance with IIS to make it
echo publically accessible on the server vis HTTPS.
echo.
echo Note that pulling django-ebagis with write-access
echo requires working SSH authorization for github. HTTPS
echo authentication is not currently supported.
echo.
echo Install command syntax:
echo.
echo ebagis.bat install instance_name postgres_user postgres_user_password
echo.
echo The instance name will be used for the database et al names.
echo The postgres user must be an andmin user and will be the database owner.
echo The password is for the databasue user. This password will also be used
echo as the password for the RabbitMQ user created for this instance.
echo.
echo These arguments must be entered in the same order shown above.
GOTO :EOF


:show_help_upgrade
echo.
echo This command will pull any updates to django-ebagis-site,
echo and django-ebagis. Additionally, all dependencies are upgraded
echo per the requirements.txt files. Lastly, any databse changes
echo are migrated.
echo.
echo To run, simply use the command below:
echo.
echo ebagis.bat upgrade
GOTO :EOF


:show_help_reset
echo.
echo This command will flush the database and load any fixtures.
echo The optional --hard flag can be used to delete and recreate
echo the database from scratch, if required.
echo.
echo To run, simply use the command below:
echo.
echo ebagis.bat reset [--hard]
GOTO :EOF


:show_help_remove
echo.
echo This command reverses the install process, deleting the
echo RabbitMQ vhost and user, the database, the conda env,
echo and the django-ebagis. The command will ask for confirmation
echo before executing. Add the --all flag to also remove the
echo directory containing this script (for complete uninstall of
echo django-ebagis-site).
echo.
echo To run, simply use the command below:
echo.
echo ebagis.bat remove[--all]
echo.
echo NOTE: --all option is currently not implemented.
GOTO :EOF


:BEGIN

::--------------------------------------------------------
::                       CONSTANTS
::--------------------------------------------------------

set arc_install_folder=C:\Program Files (x86)\ArcGIS\


::--------------------------------------------------------
::                      SCRIPT MAIN
::--------------------------------------------------------

pushd %~dp0

IF [%1]==[] (
    call:show_commands
    GOTO :END
)
IF %1==help (
    call:show_info
    echo.
    call:show_commands
    GOTO :END
)
IF %1==install (
    call:install %2,%3,%4,%5
    GOTO :END
)
IF %1==upgrade (
    call:upgrade %2
    GOTO :END
)
IF %1==reset (
    call:reset %2
    GOTO :END
)
IF %1==remove (
    call:remove %2
    GOTO :END
)
CALL :show_commands

:END
popd
GOTO :EOF


::--------------------------------------------------------
::                       FUNCTIONS
::--------------------------------------------------------

:install  -- run installation steps
::        -- %~1: name of the project instance
::        -- %~2: database/rabbitmq user
::        -- %~3: database/rabbitmq user password
::        -- %~4: option to use for IIS linking
    SETLOCAL
        IF [%~1]==[] (
            call:show_help_install
            GOTO :END
        )
        IF [%~2]==[] (
            call:show_help_install
            GOTO :END
        )
        IF [%~3]==[] (
            call:show_help_install
            GOTO :END
        )
        IF [%~1]==[help] (
            call:show_help_install
            GOTO :END
        )
        set name=%~1
        set user=%~2
        set pass=%~3
        call:set_env %name%
        call:create_celery_bat %name%
        call:get_ebagis %name%
        call:install_site_dependencies %name%
        call:create_secret_file %name%,%user%,%pass%
        call:create_database %name%,%user%,%pass%
        IF [%~4]==[--IIS] (
            call:link_to_IIS %name%
        )
        :end_install
        call:rabbitmq_setup %name%,%pass%
    ENDLOCAL
GOTO :EOF


:upgrade  -- run upgrade steps
::        -- %~1: optional help argument
    SETLOCAL
        IF [%~1]==[help] (
            call:show_help_upgrade
            GOTO :END
        )
        git pull
        call:parse_secret_file name,user,pass
        call:set_env %name%
        call:get_ebagis %name%
        call:install_site_dependencies %name%
        call:migrate_database %name%
        REM call:load_database %name%
        call:restart_celery_task %name%
        call:touch_file
        :end_upgrade
    ENDLOCAL
GOTO :EOF


:reset  -- reset database
::      -- %~1: optional argument for help/hard reset
    SETLOCAL
        IF [%~1]==[help] (
            call:show_help_reset
            GOTO :END
        )
        call:parse_secret_file name,user,pass
        IF %~1==--hard (
            call:remove_database %name%,%user%,%pass%
            call:create_database %name%,%user%,%pass%
        ) ELSE call:reset_database %name%
        call:load_database %name%
        :end_reset
    ENDLOCAL
GOTO :EOF


:remove  -- reverse installation steps
::       -- %~1: optional help argument
    SETLOCAL
        IF [%~1]==[help] (
            call:show_help_remove
            GOTO :END
        )
        call:parse_secret_file name,user,pass
        call:delink_to_IIS %name%
        call:remove_celery_bat
        call:remove_env %name%
        call:remove_ebagis
        call:remove_database %name%,%user%,%pass%
        REM The following line is to delete the whole django-ebagis-site directory
        REM IF [%~1]==[--all] ((goto) 2>nul & rmdir /s /q "%~dp0")
	IF [%~1]==[--all] (echo NOTICE: Remove --all not implemented.)
        call:rabbitmq_remove %name%
        :end_remove
    ENDLOCAL
GOTO :EOF


:rabbitmq_setup  -- create RabbitMQ vhost and user for site instance
::               -- %~1: name of vhost/user to create
::               -- %~2: user password
    SETLOCAL
        set name=%~1
        set password=%~2
        set found=False
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
    ENDLOCAL
GOTO :EOF


:rabbitmq_remove  -- remove RabbitMQ vhost and user for site instance
::                -- %~1: name of vhost/user to create
    SETLOCAL
        set name=%~1
        set found=False
        FOR /F %%i IN ('rabbitmqctl list_vhosts') DO (
            IF %%i==%name% (
        set found=True
            )
        )
        IF %found%==True (
            rabbitmqctl delete_vhost %name%
            rabbitmqctl delete_user %name%
        )
    ENDLOCAL
GOTO :EOF


:set_env  -- activate env, creating env, installing conda packages, and linking arcpy if required
::        -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name%
        IF NOT %errorlevel%==0 (
            conda create -n %name% python --file conda-requirements.txt -y
            call activate %name%
            call:create_arcpy_pthfile
        )
    ENDLOCAL
GOTO :EOF


:remove_env  -- remove a conda env
::           -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call deactivate
        conda env remove -n %name% -y
    ENDLOCAL
GOTO :EOF


:create_arcpy_pthfile  -- create the pth file to link anaconda env and arcpy lib
    SETLOCAL
        call:find_anaconda_dir anaconda_path
        call:arcgis_version arc_version_number
        SET arcpy_pth_filename=desktop%arc_version_number%.pth
        SET arcgis_path=%arc_install_folder%Desktop%arc_version_number%
        SET pthfile=%anaconda_path%\Lib\site-packages\%arcpy_pth_filename%
        @echo %arcgis_path%\bin>%pthfile%
        @echo %arcgis_path%\ArcPy>>%pthfile%
        @echo %arcgis_path%\ArcToolBox\Scripts>>%pthfile%
    ENDLOCAL
GOTO :EOF


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
GOTO :EOF


:find_anaconda_dir  -- determine path to the anaconda install directory
::                  -- %~1: return variable for dir path
    SETLOCAL
        FOR /F "usebackq tokens=1,2,4" %%i IN (`conda info`) DO (
            IF %%i==default IF %%j==environment set anaconda_path=%%k
        )
    (ENDLOCAL & REM -- RETURN VALUES
        IF "%~1" NEQ "" SET %~1=%anaconda_path%
    )
GOTO :EOF


:get_ebagis  -- pull or clone and install the django-bagis repo
::           -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        set found=0
        IF EXIST ..\django-ebagis (
            
            pushd ..\django-ebagis
            git pull
            popd

            call activate %name%
            FOR /F "usebackq" %%i IN (`pip list`) DO (
                IF %%i==django-ebagis (
                    set found=1
                )
            )
            IF %found%==0 (
                call:install_ebagis %name%
            )

        ) ELSE (
            git clone git@github.com:PSU-CSAR/django-ebagis.git ..\django-ebagis
            if %errorlevel%==0 (
                echo cloned django-ebagis with push permissions
                call:install_ebagis %name%
            ) ELSE (
                echo could not clone django-ebagis with write permissions, trying read-only
                git clone https://github.com/PSU-CSAR/django-ebagis.git ..\django-ebagis
                if %errorlevel%==0 ( 
                    call:install_ebagis %name%
                ) ELSE (
                    echo ERROR: django-ebagis could not be cloned from GitHub repo!
		    exit /b 1
                )
            )    
        )
    ENDLOCAL
GOTO :EOF


:remove_ebagis
    SETLOCAL
        echo WARNING: Any uncommitted changed to the local django-ebagis will be lost if you proceed!
        rmdir /s ..\django-ebagis
    ENDLOCAL
GOTO :EOF


:install_ebagis  -- install django-ebagis to current env in development mode
::               -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name%    
        pushd ..\django-ebagis
        pip install -r requirements.txt
        popd
    ENDLOCAL
GOTO :EOF


:install_site_dependencies
::                          -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name%
        pip install --upgrade -r requirements.txt
     ENDLOCAL
GOTO :EOF


:create_secret_file -- create the secret file with secret info for django site
::                  -- %~1: name of the project instance
::                  -- %~2: database/rabbitmq user
::                  -- %~3: database/rabbitmq user password                 
    SETLOCAL EnableDelayedExpansion
        set name=%~1
        set user=%~2
        set pass=%~3
        set secretfile=ebagis_site\secret.py

        :: cannot make this into a function because of something
        :: stupid about batch regarding delayed expansion but oh well
        set command='python -c "import random, string; print ''.join([random.SystemRandom().choice('{}{}{}'.format(string.ascii_letters, string.digits, string.punctuation.replace('\'', '').replace('\\', ''))) for i in range(50)])"'
        FOR /F %%i in (%command%) do set secret_key=%%i

        @echo SECRET_KEY = '!secret_key!'> %secretfile%
        @echo DATABASE_SETTINGS = {>> %secretfile%
        @echo     'default': {>> %secretfile%
        @echo         'ENGINE': 'django.contrib.gis.db.backends.postgis',>> %secretfile%
        @echo         'NAME': '%name%',>> %secretfile%
        @echo         'USER': '%user%',>> %secretfile%
        @echo         'PASSWORD': '%pass%',>> %secretfile%
        @echo     }>> %secretfile%
        @echo }>> %secretfile%
        @echo BROKER_URL = 'amqp://%name%:%pass%@localhost:5672/%name%'>> %secretfile%
    ENDLOCAL
GOTO :EOF


:create_database  -- check for database and create if not present
::                -- %~1: name of the database for which to check/create
::                -- %~2: admin database user to use as owner
::                -- %~3: admin database user password
    SETLOCAL
        set name=%~1
        set user=%~2
        set pass=%~3
        :: first we need to list the local databases and check for an existing one
        set found=False
        FOR /F "usebackq skip=3 tokens=1" %%i IN (`psql -d "user=%user% password=%pass% host=localhost port=5432" -c "\l"`) DO (
            IF %%i==%name% (
                set found=True
            )
        )
        :: if found is false, then we need to create the database
        if %found%==False (
            psql -d "user=%user% password=%pass% host=localhost port=5432" -c "CREATE DATABASE %name% WITH OWNER %user% TEMPLATE postgis_21 TABLESPACE gis_data"
            call:migrate_database %name%
            call:load_database %name%
        )
    ENDLOCAL
GOTO :EOF


:migrate_database  -- migrate database schema changes
::                 -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name% 
        python manage.py makemigrations
        python manage.py migrate auth
        python manage.py migrate
    ENDLOCAL
GOTO :EOF


:load_database  -- load all site fixtures into the database
::              -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name% 
        pushd ebagis_site\fixtures\
        FOR %%i in (*) do python ..\..\manage.py loaddata %%i
        popd
    ENDLOCAL
GOTO :EOF


:remove_database  -- check for database and remove if present
::                -- %~1: name of the database for which to remove
::                -- %~2: admin database user to use as owner
::                -- %~3: admin database user password
    SETLOCAL
        set name=%~1
        set user=%~2
        set pass=%~3
        psql -d "user=%user% password=%pass% host=localhost port=5432" -c "DROP DATABASE IF EXISTS %name%"
    ENDLOCAL
GOTO :EOF


:reset_database
::               -- %~1: name for the environment
    SETLOCAL
        set name=%~1
        call activate %name% 
        python manage.py flush
        call:load_database %name%
  ENDLOCAL
GOTO :EOF


:parse_secret_file  -- extract the instance name, database username, and DB user password from secret file
::                  -- %~1: return variable for instance name
::                  -- %~2: return variable for database user
::                  -- %~3: return variable for database user password
    SETLOCAL
        FOR /f "tokens=1,2 skip=3 delims=,:' " %%A IN (ebagis_site\secret.py) DO (
            IF %%A==NAME set name=%%B
            IF %%A==USER set user=%%B
            IF %%A==PASSWORD set pass=%%B
        )
    (ENDLOCAL & REM -- RETURN VALUES
        IF "%~1" NEQ "" SET %~1=%name%
        IF "%~2" NEQ "" SET %~2=%user%
        IF "%~3" NEQ "" SET %~3=%pass%
    )
GOTO :EOF


:link_to_IIS  -- link this instance ot IIS
::            -- %~1: instance name used for IIS site name
    SETLOCAL
        set name=%~1
        call:setup_static_assets %name%

        :: add the site to IIS using the django-windows-tools command
        set touch_file=%~dp0touch_this_to_update_cgi.txt
        call activate %name%
        python manage.py winfcgi_install --site-name %name% --monitor-changes-to %touch_file% --binding=https://*:443

        :: add max upload setting of 1GB to web.config file 
        set cfg_str='    ^<security^>\n      ^<requestFiltering^>\n         ^<requestLimits maxAllowedContentLength=\"1024000000\"/^>\n      ^</requestFiltering^>\n    ^</security^>\n'
        set cfg='web.config'
        python -c "f=open(%cfg%); content=[l for l in f]; f.close(); content.insert(3, %cfg_str%); f=open(%cfg%,'w'); f.write(''.join(content)); f.close()"

        :: set permissions on the django-ebagis-site directory for IIS site user
        pushd ..
        ICACLS django-ebagis-site /t  /grant "IIS AppPool\%name%":F
        popd

        :: link celery script to system task
        call:create_celery_task %name%
    ENDLOCAL
GOTO :EOF


:setup_static_assets  -- collect the static assets and create config file
::                    -- %~1: name of the python env for the project instance
    SETLOCAL
        set name=%~1

        :: collect the static assets for the site
        call activate %name%
        python manage.py collectstatic

        :: add a configuration file to the static asset dir for IIS
        set static_config=static\web.config
        IF NOT EXIST %static_config% (
            @echo ^<?xml version="1.0" encoding="UTF-8"?^>> %static_config%
            @echo ^<configuration^>>> %static_config%
            @echo   ^<system.webServer^>>> %static_config%
            @echo     ^<^^!-- this configuration overrides the FastCGI handler to let IIS serve the static files --^>>> %static_config%
            @echo     ^<handlers^>>> %static_config%
            @echo     ^<clear/^>>> %static_config%
            @echo       ^<add name="StaticFile" path="*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" /^>>> %static_config%
            @echo     ^</handlers^>>> %static_config%
            @echo   ^</system.webServer^>>> %static_config%
            @echo ^</configuration^>>> %static_config%
        )
    ENDLOCAL
GOTO :EOF


:delink_to_IIS  -- remove a site on IIS
::              -- %~1: name of IIS site to be removed
    SETLOCAL
        set name=%~1
        call activate %name%
        python manage.py winfcgi_install --delete --site-name %name%
        call:remove_celery_task %name%
        rmdir /q /s static\
    ENDLOCAL
GOTO :EOF     


:create_celery_bat  -- creates the bat file for launching celery
::                  -- %~1: name of the anaconda env to activate
    SETLOCAL
        set name=%~1
        set celery_bat=start_celery.bat
        @echo @echo off> %celery_bat%
        @echo pushd %%~dp0>> %celery_bat%
        @echo call activate %name%>> %celery_bat%
        @echo celery -A ebagis_site worker -l info --logfile %%~dp0\celery.log --pidfile %%~dp0\celery.pid>> %celery_bat%
    ENDLOCAL
GOTO :EOF


:remove_celery_bat  -- removes the bat file for launching celery
    SETLOCAL
        del start_celery.bat
    ENDLOCAL
GOTO :EOF


:create_celery_task  -- link the celery bat file to a scheduled task
::                   -- %~1: name of project instance (for task name)
    SETLOCAL
        set name=%~1
        set celery_bat=start_celery.bat
        schtasks /create /tn %name%_celery /tr %~dp0%celery_bat% /sc onstart /ru SYSTEM
        schtasks /run /tn %name%_celery
    ENDLOCAL
GOTO :EOF


:remove_celery_task  -- remove the task running celery for an IIS site
::                   -- %~1: name of task to remove
    SETLOCAL
        set name=%~1
        schtasks /end /tn %name%_celery
        schtasks /delete /f /tn %name%_celery
    ENDLOCAL
GOTO :EOF


:restart_celery_task  -- restart a system celery task if it exists
::                    -- %~1: the name of the project instance
    SETLOCAL
       set name=%~1
       schtasks /end /tn %name%_celery
       schtasks /run /tn %name%_celery
    ENDLOCAL
GOTO :EOF


:touch_file
    SETLOCAL
        echo. 2>touch_this_to_update_cgi.txt
    ENDLOCAL
GOTO :EOF
