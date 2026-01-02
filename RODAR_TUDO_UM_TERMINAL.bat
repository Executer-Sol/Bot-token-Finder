@echo off
chcp 65001 >nul
echo ======================================================================
echo    Bot Trading - TUDO EM UM TERMINAL
echo ======================================================================
echo.
echo Isso vai rodar Interface Web + Bot no mesmo terminal
echo.
echo Interface Web: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar TUDO
echo.
echo ======================================================================
echo.

cd /d "%~dp0"

python run_all.py

pause
