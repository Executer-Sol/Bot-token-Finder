@echo off
echo ========================================
echo   PUBLICAR PROJETO NO GITHUB
echo ========================================
echo.

REM Verificar se Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git nao esta instalado!
    echo Baixe em: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] Verificando arquivos sensiveis...
if exist .env (
    echo [AVISO] Arquivo .env encontrado!
    echo Verifique se esta no .gitignore
    git check-ignore .env >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] .env NAO esta no .gitignore!
        echo Adicione .env ao .gitignore antes de continuar
        pause
        exit /b 1
    ) else (
        echo [OK] .env esta sendo ignorado corretamente
    )
)

echo.
echo [2/5] Adicionando arquivos...
git add .
if errorlevel 1 (
    echo [ERRO] Falha ao adicionar arquivos
    pause
    exit /b 1
)

echo.
echo [3/5] Verificando o que sera commitado...
git status --short
echo.
set /p confirm="Deseja continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Cancelado pelo usuario
    pause
    exit /b 0
)

echo.
echo [4/5] Fazendo commit...
set /p commit_msg="Digite a mensagem do commit (ou Enter para usar padrao): "
if "%commit_msg%"=="" set commit_msg=Atualizacao do projeto - Bot de Trading Solana
git commit -m "%commit_msg%"
if errorlevel 1 (
    echo [ERRO] Falha ao fazer commit
    pause
    exit /b 1
)

echo.
echo [5/5] Verificando se tem repositorio remoto...
git remote -v >nul 2>&1
if errorlevel 1 (
    echo.
    echo [AVISO] Nenhum repositorio remoto configurado!
    echo.
    echo Para conectar ao GitHub:
    echo 1. Crie um repositorio em: https://github.com/new
    echo 2. Execute o comando:
    echo    git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
    echo 3. Execute novamente este script
    echo.
    pause
    exit /b 0
)

echo.
echo Enviando para o GitHub...
git push
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao enviar para GitHub
    echo.
    echo Possiveis causas:
    echo - Nao esta autenticado (crie um token em: https://github.com/settings/tokens)
    echo - Repositorio nao existe ou nao tem permissao
    echo - Branch diferente (tente: git push -u origin main)
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCESSO! Projeto publicado no GitHub
echo ========================================
echo.
pause

