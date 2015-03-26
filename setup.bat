@echo off

Setlocal EnableDelayedExpansion


REM *****constants******
REM --------------------
set anaconda_path=C:\Anaconda_x86
set arcgis_path=C:\Program Files (x86)\ArcGIS\Desktop10.3
set arcpy_pth_filename=desktop10.3.pth


REM create secret key
REM -----------------
set command='python -c "import random, string; print ''.join([random.SystemRandom().choice('{}{}{}'.format(string.ascii_letters, string.digits, string.punctuation.replace('\'', '').replace('\\', ''))) for i in range(50)])"'
for /f %%i in (%command%) do set SECRET_KEY=%%i


REM clone the django-bagis repo
REM ---------------------------
git clone git@github.com:PSU-CSAR/django-ebagis.git ../django-ebagis && (
  echo cloned django-ebagis with push permissions
) || (
  echo could not clone django-ebagis with push; trying read-only
  git clone https://github.com/PSU-CSAR/django-ebagis.git ../django-ebagis
)


REM create env and install conda packages
REM -------------------------------------
conda create -n %1 python --file conda-requirements.txt
call activate %1


REM install pip dependencies
REM ------------------------
set OLDDIR=%CD%
cd ../django-ebagis
pip install -r ../django-ebagis/requirements.txt
cd %OLDDIR%
pip install -r requirements.txt


REM create database
REM ---------------
echo %3 | createdb -U %2 -D gis_data -T postgis_21 %1


REM create secret file
REM ------------------
set secretfile=ebagis_site\secret.py
@echo SECRET_KEY = '!SECRET_KEY!' > %secretfile%
@echo DATABASE_SETTINGS = { >> %secretfile%
@echo     'default': { >> %secretfile%
@echo         'ENGINE': 'django.contrib.gis.db.backends.postgis', >> %secretfile%
@echo         'NAME': '%1', >> %secretfile%
@echo         'USER': '%2', >> %secretfile%
@echo         'PASSWORD': '%3' >> %secretfile%
@echo     } >> %secretfile%
@echo } >> %secretfile%


REM copy pth file for arcpy
REM -----------------------
set pthfile=%anaconda_path%\envs\%1\Lib\site-packages\%arcpy_pth_filename%
@echo %arcgis_path%\bin>%pthfile%
@echo %arcgis_path%\ArcPy>>%pthfile%
@echo %arcgis_path%\ArcToolBox\Scripts>>%pthfile%


REM create batch file for celery task
REM ---------------------------------
REM set env_python=%anaconda_path%\envs\%1\python.exe
REM @echo %env_python% -m celery.bin.celeryd>start_celery.bat


REM migrate database and load user fixtures
REM ---------------------------------------
python manage.py flush
python manage.py migrate
python manage.py loaddata ebagis_site\fixtures\user_fixtures.json
