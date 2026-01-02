@echo off
chcp 65001 >nul
echo ======================================================================
echo    Iniciando Bot Trading + Interface Web
echo ======================================================================
echo.
echo Iniciando em 2 janelas separadas:
echo   1. Interface Web (http://localhost:5000)
echo   2. Bot Trading (servidor)
echo.
echo ======================================================================
echo.

cd /d "%~dp0"

REM Inicia interface web em nova janela
start "Interface Web - Bot Trading" cmd /k "python web_interface.py"

REM Aguarda 3 segundos
timeout /t 3 /nobreak >nul

REM Inicia bot em nova janela
start "Bot Trading - Servidor" cmd /k "python run_bot_server.py"

echo.
echo ======================================================================
echo   Ambos os servicos foram iniciados!
echo.
echo   Interface Web: http://localhost:5000
echo   Bot: Rodando em background
echo.
echo   Feche esta janela quando quiser
echo ======================================================================
pause

