@echo off
echo ============================================================
echo REINICIANDO INTERFACE WEB
echo ============================================================
echo.
echo Parando processos Python antigos...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Interface Web*" 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Iniciando interface web atualizada...
start "Interface Web" cmd /k "cd /d %~dp0 && python run_web.py"
echo.
echo Interface web reiniciada!
echo Acesse: http://localhost:5000
echo.
echo Pressione qualquer tecla para fechar...
pause >nul

