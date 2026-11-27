@echo off
setlocal
cd /d "%~dp0" || exit /b 1

call instalar_controladores.bat --no-pause || goto :error
".venv\Scripts\python.exe" manage.py migrate --noinput || goto :error

if not defined XINCRONIX_BIND set "XINCRONIX_BIND=127.0.0.1:8000"
echo Xincronix: http://%XINCRONIX_BIND%/ ^(Ctrl+C para detenerlo^)
".venv\Scripts\python.exe" manage.py runserver "%XINCRONIX_BIND%" || goto :error
exit /b 0

:error
echo No se pudo iniciar Xincronix. Revisa el error anterior.
if /i not "%~1"=="--no-pause" pause
exit /b 1
