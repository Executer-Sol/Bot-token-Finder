@echo off
chcp 65001 >nul
echo ======================================================================
echo    Bot Trading - Modo Servidor
echo ======================================================================
echo.
echo O bot vai rodar continuamente em background
echo Acesse http://localhost:5000 para controlar via interface web
echo.
echo Pressione Ctrl+C para parar
echo.
echo ======================================================================
echo.
cd /d "%~dp0"
python run_bot_server.py
pause

