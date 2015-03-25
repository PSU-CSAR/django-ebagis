@echo off

Setlocal EnableDelayedExpansion

REM create secret key
set command='python -c "import random, string; print ''.join([random.SystemRandom().choice('{}{}{}'.format(string.ascii_letters, string.digits, string.punctuation.replace('\'', '').replace('\\', ''))) for i in range(50)])"'
echo %command%
for /f %%i in (%command%) do set SECRET_KEY=%%i

REM clone the django-bagis repo
git clone git@github.com:PSU-CSAR/django-ebagis.git ../django-ebagis && (
  echo cloned django-ebagis with push permissions
) || (
  echo could not clone django-ebagis with push; trying read-only
  git clone https://github.com/PSU-CSAR/django-ebagis.git ../django-ebagis
)

REM create env and install conda packages
conda create -n %1 python --file conda-requirements.txt
call activate %1

REM install pip dependencies
set OLDDIR=%CD%
cd ../django-ebagis
pip install -r ../django-ebagis/requirements.txt
cd %OLDDIR%
pip install -r requirements.txt

REM create database
echo %3 | createdb -U %2 -D gis_data -T postgis_21 %1

REM create secret file
set secretfile=ebagis_site\secret.py
echo %secretfile%
echo %secretfile%
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
set pthfile=C:\Anaconda_x86\envs\%1\Lib\site-packages\desktop10.3.pth
@echo C:\Program Files (x86)\ArcGIS\Desktop10.3\bin>%pthfile%
@echo C:\Program Files (x86)\ArcGIS\Desktop10.3\ArcPy>>%pthfile%
@echo C:\Program Files (x86)\ArcGIS\Desktop10.3\ArcToolBox\Scripts>>%pthfile%

REM migrate database and load users
python manage.py migrate
python manage.py loaddata ebagis_site\fixtures\user_fixtures.json
