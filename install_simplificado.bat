@echo off
echo ========================================
echo Instalando Sistema VanCheck Simplificado
echo ========================================
echo.

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando Django...
pip install django==4.2.0

echo Instalando bibliotecas basicas...
pip install opencv-python-headless
pip install numpy
pip install qrcode[pil]
pip install pillow
pip install requests

echo Instalando MediaPipe versao compativel...
pip uninstall mediapipe -y
pip install mediapipe==0.10.3

echo.
echo Criando estrutura de pastas...
mkdir apps\checkin\migrations 2>nul
mkdir apps\ocorrencias\migrations 2>nul
mkdir templates\checkin 2>nul
mkdir templates\ocorrencias 2>nul
mkdir static\css 2>nul
mkdir static\js 2>nul
mkdir static\sounds 2>nul
mkdir media 2>nul
mkdir logs 2>nul

echo.
echo Criando arquivos __init__.py...
echo. > apps\__init__.py
echo. > apps\checkin\__init__.py
echo. > apps\checkin\migrations\__init__.py
echo. > apps\ocorrencias\__init__.py
echo. > apps\ocorrencias\migrations\__init__.py
echo. > config\__init__.py

echo.
echo Removendo banco antigo...
del db.sqlite3 2>nul

echo.
echo Criando migrations...
python manage.py makemigrations checkin
python manage.py makemigrations ocorrencias
python manage.py migrate

echo.
echo Criando superusuario...
python manage.py createsuperuser

echo.
echo ========================================
echo Instalacao concluida!
echo Execute: python manage.py runserver
echo ========================================
pause