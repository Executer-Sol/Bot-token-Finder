# Solução para Problema de DNS com Jupiter API

## Problema
O domínio `quote-api.jup.ag` não está sendo resolvido pelo DNS atual.

## Solução: Mudar DNS para Google ou Cloudflare

### Método 1: Via Interface Gráfica do Windows

1. **Abra as Configurações de Rede:**
   - Clique com botão direito no ícone de Wi-Fi/Rede na barra de tarefas
   - Ou vá em: Configurações > Rede e Internet > Wi-Fi (ou Ethernet)

2. **Acesse as Propriedades do Adaptador:**
   - Clique em "Alterar opções do adaptador"
   - Clique com botão direito no adaptador ativo (Wi-Fi ou Ethernet)
   - Selecione "Propriedades"

3. **Configure o DNS:**
   - Selecione "Protocolo TCP/IPv4" (ou "Internet Protocol Version 4")
   - Clique em "Propriedades"
   - Marque "Usar os seguintes endereços de servidor DNS"
   - DNS preferencial: `8.8.8.8` (Google)
   - DNS alternativo: `8.8.4.4` (Google)
   - OU use Cloudflare: `1.1.1.1` e `1.0.0.1`
   - Clique em "OK"

4. **Limpe o Cache DNS:**
   - Abra PowerShell como Administrador
   - Execute: `ipconfig /flushdns`

5. **Teste novamente:**
   ```powershell
   python diagnostico_dns.py
   ```

### Método 2: Via PowerShell (Administrador)

```powershell
# Ver adaptadores de rede
Get-NetAdapter

# Substitua "Wi-Fi" pelo nome do seu adaptador
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ServerAddresses "8.8.8.8","8.8.4.4"

# Limpar cache DNS
Clear-DnsClientCache

# Testar
python diagnostico_dns.py
```

### Método 3: Temporário (apenas esta sessão)

Se não conseguir mudar o DNS do sistema, pode tentar usar um proxy DNS temporário, mas isso não é recomendado para uso em produção.

## Após Mudar DNS

Execute novamente:
```powershell
python teste_solana_simples.py
```

## Verificação

Execute o diagnóstico:
```powershell
python diagnostico_dns.py
```

Deve aparecer:
```
OK: quote-api.jup.ag -> [endereço IP]
```

## Notas

- Mudar DNS é seguro e comum
- DNS do Google (8.8.8.8) é confiável e rápido
- Você pode voltar ao DNS automático depois se quiser
- Isso não afeta sua segurança ou privacidade de forma significativa

