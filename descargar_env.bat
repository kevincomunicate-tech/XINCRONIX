@echo off
setlocal
cd /d "%~dp0" || exit /b 1

if exist ".env" (
    echo El archivo .env ya existe.
    goto :fin
)
if not exist ".env.example" (
    echo Falta .env.example. Descarga el repositorio completo.
    goto :error
)
copy /-y ".env.example" ".env" >nul || goto :error
echo Se creo .env desde .env.example. Configura tus credenciales alli si necesitas las integraciones.

:fin
if /i not "%~1"=="--no-pause" pause
exit /b 0

:error
if /i not "%~1"=="--no-pause" pause
exit /b 1
