# Script para mudar DNS para Google (8.8.8.8)
# Execute como Administrador: PowerShell -ExecutionPolicy Bypass -File mudar_dns.ps1

Write-Host "================================================================================"
Write-Host "  MUDANDO DNS PARA GOOGLE (8.8.8.8)"
Write-Host "================================================================================"
Write-Host ""

# Verifica se está rodando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Como executar:"
    Write-Host "1. Clique com botao direito no PowerShell"
    Write-Host "2. Selecione 'Executar como administrador'"
    Write-Host "3. Navegue ate a pasta: cd '$PSScriptRoot'"
    Write-Host "4. Execute: .\mudar_dns.ps1"
    Write-Host ""
    pause
    exit 1
}

# Lista adaptadores ativos
Write-Host "Adaptadores de rede ativos:"
Write-Host ""
$adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
$adapters | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""

# Pede qual adaptador mudar
if ($adapters.Count -eq 1) {
    $adapterName = $adapters[0].Name
    Write-Host "Usando adaptador: $adapterName" -ForegroundColor Green
} else {
    Write-Host "Qual adaptador voce quer configurar? (digite o nome exato)"
    $adapterName = Read-Host "Adaptador"
    
    if (-not (Get-NetAdapter -Name $adapterName -ErrorAction SilentlyContinue)) {
        Write-Host "ERRO: Adaptador '$adapterName' nao encontrado!" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "Configurando DNS para Google (8.8.8.8 e 8.8.4.4)..." -ForegroundColor Yellow

try {
    # Muda DNS para Google
    Set-DnsClientServerAddress -InterfaceAlias $adapterName -ServerAddresses "8.8.8.8","8.8.4.4" -ErrorAction Stop
    Write-Host "DNS configurado com sucesso!" -ForegroundColor Green
    Write-Host ""
    
    # Limpa cache DNS
    Write-Host "Limpando cache DNS..." -ForegroundColor Yellow
    Clear-DnsClientCache
    Write-Host "Cache limpo!" -ForegroundColor Green
    Write-Host ""
    
    # Testa resolução
    Write-Host "Testando resolucao de DNS..." -ForegroundColor Yellow
    try {
        $ip = [System.Net.Dns]::GetHostAddresses("quote-api.jup.ag")[0].IPAddressToString
        Write-Host "SUCESSO! quote-api.jup.ag resolve para: $ip" -ForegroundColor Green
        Write-Host ""
        Write-Host "DNS configurado corretamente!" -ForegroundColor Green
    } catch {
        Write-Host "AVISO: Ainda nao conseguiu resolver quote-api.jup.ag" -ForegroundColor Yellow
        Write-Host "Tente novamente em alguns segundos ou reinicie o computador" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "================================================================================"
    Write-Host "  DNS CONFIGURADO!"
    Write-Host "================================================================================"
    Write-Host ""
    Write-Host "Agora voce pode executar:"
    Write-Host "  python diagnostico_dns.py"
    Write-Host "  python teste_solana_simples.py"
    Write-Host ""
    
} catch {
    Write-Host "ERRO ao configurar DNS: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tente fazer manualmente:"
    Write-Host "1. Configuracoes > Rede e Internet"
    Write-Host "2. Alterar opcoes do adaptador"
    Write-Host "3. Clique com botao direito no adaptador > Propriedades"
    Write-Host "4. Protocolo TCP/IPv4 > Propriedades"
    Write-Host "5. Use os seguintes enderecos DNS: 8.8.8.8 e 8.8.4.4"
    Write-Host ""
}

pause











