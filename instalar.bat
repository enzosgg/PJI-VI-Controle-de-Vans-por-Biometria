@echo off
echo ========================================
echo Instalando Sistema VanCheck
echo ========================================
echo.

echo 1. Instalando dependencias...
pip install django==4.2.0
pip install opencv-python
pip install mediapipe
pip install numpy
pip install qrcode[pil]
pip install pillow
pip install requests

echo.
echo 2. Criando estrutura de pastas...
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
echo 3. Criando arquivos __init__.py...
echo. > apps\__init__.py
echo. > apps\checkin\__init__.py
echo. > apps\checkin\migrations\__init__.py
echo. > apps\ocorrencias\__init__.py
echo. > apps\ocorrencias\migrations\__init__.py
echo. > config\__init__.py

echo.
echo 4. Criando migrations...
python manage.py makemigrations checkin
python manage.py makemigrations ocorrencias
python manage.py migrate

echo.
echo 5. Criando superusuario...
python manage.py createsuperuser

echo.
echo ========================================
echo Instalacao concluida!
echo Execute: python manage.py runserver
echo ========================================
pause