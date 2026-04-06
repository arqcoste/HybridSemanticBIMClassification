@echo off
echo ================================================
echo  Hybrid BIM Classification Engine — Setup
echo ================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo Descargalo desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

echo Instalando dependencias...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Hubo un problema instalando dependencias.
    pause
    exit /b 1
)

echo.
echo ================================================
echo  Setup completado correctamente.
echo  Ejecuta run.bat para iniciar la aplicacion.
echo ================================================
pause
