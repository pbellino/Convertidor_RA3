@echo off
echo ==========================================
echo Compilando Convertidor RA3 para Windows...
echo ==========================================

:: 1. Activar el entorno virtual si existe (ajustar nombre si no es 'venv')
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ADVERTENCIA] No se encontro venv\Scripts\activate.bat. 
    echo Asegurate de tener las dependencias instaladas globalmente o en tu venv.
)

:: 2. Obtener el hash corto de git
for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set SHA_SHORT=%%i

:: 3. Definir version (puedes cambiarla manualmente o automatizarla)
set VERSION=v0.0.4

:: 4. Ejecutar PyInstaller
:: Nota: Usamos ';' para separar los datos en Windows
pyinstaller --noconfirm --onefile --windowed ^
    --icon="ra3.ico" ^
    --name "Convertidor_RA3_Win_%VERSION%_%SHA_SHORT%" ^
    --add-data "io_sead.py;." ^
    --collect-all ttkbootstrap ^
    --hidden-import pandas ^
    --collect-submodules PIL ^
    "convertidor_RA3.py"

echo.
echo ==========================================
echo Proceso finalizado. El .exe esta en /dist
echo ==========================================
pause
