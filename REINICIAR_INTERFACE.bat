@echo off
chcp 65001 >nul
echo ======================================================================
echo    Reiniciando Interface Web
echo ======================================================================
echo.
echo Parando processos Python na porta 5000...
echo.

cd /d "%~dp0"

REM Mata processos na porta 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo Iniciando interface web...
echo.
echo Acesse: http://localhost:5000
echo Pressione Ctrl+C para parar
echo.
echo ======================================================================
echo.

python web_interface.py

pause

