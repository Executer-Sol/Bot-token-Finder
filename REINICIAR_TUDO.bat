@echo off
echo ============================================================
echo REINICIANDO TUDO (Bot + Interface Web)
echo ============================================================
echo.
echo Parando todos os processos Python...
taskkill /F /IM python.exe 2>nul
timeout /t 3 /nobreak >nul
echo.
echo Iniciando Bot + Interface Web atualizados...
cd /d %~dp0
python run_all.py
pause
