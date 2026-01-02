@echo off
echo Parando processos Python existentes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Removendo arquivo journal da sessao (se existir)...
if exist session.session-journal del /F /Q session.session-journal
echo.
echo Pronto! Agora voce pode rodar o bot.
pause


