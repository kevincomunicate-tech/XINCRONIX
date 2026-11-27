@echo off
setlocal
cd /d "%~dp0" || exit /b 1

call descargar_env.bat --no-pause || goto :error
if exist ".venv\Scripts\python.exe" goto :dependencias

for %%V in (3.13 3.14 3.12 3.11) do (
    py -%%V -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        py -%%V -m venv .venv || goto :error
        goto :dependencias
    )
)
python -c "import sys; sys.exit(not ((3, 11) <= sys.version_info[:2] <= (3, 14)))" >nul 2>&1
if errorlevel 1 (
    echo Instala Python 3.11 a 3.14 y agregalo al PATH. Se recomienda Python 3.13.
    goto :error
)
python -m venv .venv || goto :error

:dependencias
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt || goto :error
".venv\Scripts\python.exe" -c "import os, subprocess, sys; from dotenv import load_dotenv; load_dotenv('.env'); motor = os.getenv('DB_ENGINE', 'sqlite').strip().lower(); driver = {'sqlite': '', 'mysql': 'mysqlclient==2.3.1', 'postgresql': 'psycopg[binary]>=3.1.12,<4'}.get(motor); sys.exit('DB_ENGINE debe ser sqlite, mysql o postgresql.' if driver is None else (subprocess.call([sys.executable, '-m', 'pip', 'install', driver]) if driver else 0))" || goto :error
echo Dependencias listas.
if /i not "%~1"=="--no-pause" pause
exit /b 0

:error
echo No se pudo preparar el entorno. Revisa el error anterior.
if /i not "%~1"=="--no-pause" pause
exit /b 1
