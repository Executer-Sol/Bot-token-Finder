@echo off
chcp 65001 >nul
title Interface Web - Bot Trading
cd /d "%~dp0"
python web_interface.py
pause

