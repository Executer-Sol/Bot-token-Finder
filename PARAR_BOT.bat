@echo off
echo Parando processos Python do bot...
taskkill /F /FI "WINDOWTITLE eq *bot*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *bot.py*" 2>nul
timeout /t 2 /nobreak >nul
echo Bot parado. Agora você pode iniciar novamente.

