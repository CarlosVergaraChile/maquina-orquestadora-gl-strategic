@echo off
REM Orquesta IA - Windows Startup Script
REM Para el Lenovo T495 con AMD Ryzen PRO

echo ========================================
echo Iniciando Orquesta IA...
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado.
    echo Por favor, descargue Python desde: https://www.python.org/downloads/
    echo Asegúrese de marcar "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Crear entorno virtual si no existe
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

echo [OK] Entorno virtual activado
echo.

REM Instalar dependencias si es necesario
echo Instalando dependencias (esto puede tomar un momento)...
pip install -q -r requirements.txt

echo [OK] Dependencias instaladas
echo.

REM Crear archivo .env si no existe
if not exist .env (
    echo Creando archivo de configuración...
    copy .env.example .env >nul
    echo [OK] Archivo .env creado - Por favor, edita .env con tu API key de Claude
    echo.
    echo IMPORTANTE: Abre el archivo .env y reemplaza:
    echo   CLAUDE_API_KEY=tu_api_key_aqui
    echo.
    pause
)

echo ========================================
echo Iniciando servidor Orquesta...
echo ========================================
echo.
echo La Orquesta estará disponible en:
echo   http://localhost:8000/app
echo.
echo Abre tu navegador y ve a esa dirección.
echo Presiona CTRL+C en esta ventana para detener el servidor.
echo.

REM Iniciar el servidor
cd app/backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

pause
