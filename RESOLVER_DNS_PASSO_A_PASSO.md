# Como Resolver o Problema de DNS - Passo a Passo

## 🔍 Problema
O domínio `quote-api.jup.ag` não está sendo resolvido pelo DNS, impedindo o bot de conectar à API do Jupiter.

## ✅ Solução: Mudar DNS para Google (8.8.8.8)

### Método 1: Via Interface Gráfica do Windows (RECOMENDADO)

#### Passo 1: Abrir Configurações de Rede
1. Pressione `Win + I` (tecla Windows + I)
2. Ou clique no menu Iniciar > ⚙️ Configurações

#### Passo 2: Ir para Rede e Internet
1. Clique em **"Rede e Internet"**
2. No menu lateral, clique em **"Ethernet"** (ou "Wi-Fi" se você usa Wi-Fi)

#### Passo 3: Acessar Propriedades do Adaptador
1. Role a página até encontrar **"Configurações de rede relacionadas"**
2. Clique em **"Alterar opções do adaptador"**
3. Uma nova janela vai abrir mostrando seus adaptadores de rede

#### Passo 4: Abrir Propriedades do Adaptador Ativo
1. Encontre o adaptador ativo (geralmente mostra "Ethernet" ou "Wi-Fi")
2. Clique com o **botão direito** nele
3. Selecione **"Propriedades"**

#### Passo 5: Configurar DNS
1. Na lista de itens, encontre **"Protocolo TCP/IPv4"** ou **"Internet Protocol Version 4"**
2. Clique nele para selecionar
3. Clique no botão **"Propriedades"**

#### Passo 6: Definir DNS Manualmente
1. Marque a opção: **"Usar os seguintes endereços de servidor DNS"**
2. No campo **"Servidor DNS preferencial"**: digite `8.8.8.8`
3. No campo **"Servidor DNS alternativo"**: digite `8.8.4.4`
4. Clique em **"OK"**
5. Clique em **"Fechar"** na janela de propriedades

#### Passo 7: Limpar Cache DNS
1. Abra **PowerShell como Administrador**:
   - Clique no menu Iniciar
   - Digite "PowerShell"
   - Clique com botão direito em "Windows PowerShell"
   - Selecione **"Executar como administrador"**

2. Execute o comando:
```powershell
ipconfig /flushdns
```

3. Você deve ver: "Liberação do Cache do DNS Resolver bem-sucedida."

#### Passo 8: Testar
Volte para o PowerShell normal e execute:
```powershell
cd C:\Users\je222\telegram_trading_bot
python diagnostico_dns.py
```

Deve aparecer:
```
OK: quote-api.jup.ag -> [endereço IP]
```

---

### Método 2: Via PowerShell (Como Administrador)

Se preferir fazer via linha de comando:

1. **Abra PowerShell como Administrador**:
   - Menu Iniciar > Digite "PowerShell" > Botão direito > "Executar como administrador"

2. **Descubra o nome do seu adaptador**:
```powershell
Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object Name
```

3. **Configure o DNS** (substitua "Ethernet" pelo nome do seu adaptador):
```powershell
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "8.8.8.8","8.8.4.4"
```

4. **Limpe o cache DNS**:
```powershell
Clear-DnsClientCache
```

5. **Teste**:
```powershell
cd C:\Users\je222\telegram_trading_bot
python diagnostico_dns.py
```

---

## 🔄 Se Ainda Não Funcionar

### Opção 1: Reiniciar o Computador
Muitas vezes o Windows precisa de um reinício para aplicar completamente as mudanças de DNS.

1. Reinicie o computador
2. Após reiniciar, teste novamente: `python diagnostico_dns.py`

### Opção 2: Tentar Outro DNS
Se o Google DNS não funcionar, tente Cloudflare:

**Via Interface Gráfica:**
- DNS preferencial: `1.1.1.1`
- DNS alternativo: `1.0.0.1`

**Via PowerShell:**
```powershell
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "1.1.1.1","1.0.0.1"
Clear-DnsClientCache
```

### Opção 3: Usar VPN
Se for bloqueio do seu provedor de internet (ISP), use uma VPN:
- Ative uma VPN (ExpressVPN, NordVPN, ProtonVPN, etc.)
- Teste novamente: `python diagnostico_dns.py`

### Opção 4: Testar de Outra Rede
- Use hotspot do celular
- Use outra rede Wi-Fi
- Teste: `python diagnostico_dns.py`

---

## ⚠️ Problemas Comuns

### "Não tenho permissão"
- Você precisa executar PowerShell como **Administrador**
- Clique direito > "Executar como administrador"

### "Adaptador não encontrado"
- Verifique o nome exato com: `Get-NetAdapter`
- O nome deve ser exatamente igual (inclui maiúsculas/minúsculas)

### "Ainda não funciona após mudar DNS"
1. Reinicie o computador
2. Verifique se o DNS está realmente configurado:
   ```powershell
   Get-DnsClientServerAddress -InterfaceAlias "Ethernet"
   ```
3. Deve mostrar: `8.8.8.8` e `8.8.4.4`

---

## ✅ Verificação Final

Depois de configurar, execute:
```powershell
python diagnostico_dns.py
```

Se aparecer:
```
OK: quote-api.jup.ag -> [endereço IP]
```

**Parabéns! O DNS está funcionando!** 🎉

Agora você pode testar o bot:
```powershell
python teste_solana_simples.py
```

---

## 💡 Por que isso acontece?

- Alguns provedores de internet (ISP) têm DNS que não conseguem resolver todos os domínios
- DNS do Google (8.8.8.8) e Cloudflare (1.1.1.1) são mais confiáveis e rápidos
- É seguro usar esses DNS públicos
- Você pode voltar ao DNS automático depois se quiser











