@echo off
chcp 65001 >nul
title Bot Trading
cls

echo.
echo ======================================================================
echo    Bot Trading - TUDO EM UM TERMINAL
echo ======================================================================
echo.
echo Interface Web: http://localhost:5000
echo Bot: Monitorando Telegram
echo.
echo Pressione Ctrl+C para parar TUDO
echo.
echo ======================================================================
echo.

cd /d "%~dp0"

python run_all.py

echo.
echo Bot parado.
pause
