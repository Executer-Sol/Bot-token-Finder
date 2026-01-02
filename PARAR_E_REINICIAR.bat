@echo off
echo ============================================================
echo PARANDO servidor web antigo e reiniciando tudo
echo ============================================================
echo.
echo Parando processo na porta 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo Matando processo PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo.
echo Parando todos os processos Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo.
echo Iniciando Bot + Interface Web atualizados...
cd /d %~dp0
python run_all.py
pause

