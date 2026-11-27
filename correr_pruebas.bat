@echo off
setlocal
cd /d "%~dp0" || exit /b 1

rem Las pruebas usan SQLite en memoria, incluso si el entorno local apunta a otro motor.
set "DB_ENGINE=sqlite"
set "SQLITE_FILE=:memory:"
call instalar_controladores.bat --no-pause || goto :error
".venv\Scripts\python.exe" manage.py test --noinput || goto :error
echo Todas las pruebas pasaron.
if /i not "%~1"=="--no-pause" pause
exit /b 0

:error
echo Las pruebas no se completaron correctamente. Revisa el detalle anterior.
if /i not "%~1"=="--no-pause" pause
exit /b 1
