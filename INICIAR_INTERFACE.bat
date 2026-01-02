@echo off
chcp 65001 >nul
echo ======================================================================
echo    Iniciando Interface Web
echo ======================================================================
echo.
cd /d "%~dp0"
python web_interface.py
pause
