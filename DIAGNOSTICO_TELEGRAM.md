# 🔍 Diagnóstico: Bot não detecta mensagens do Telegram

## ✅ Verificações Básicas

### 1. Bot está rodando?
- Verifique se o bot está ativo no terminal
- Deve mostrar: `✅ Bot conectado ao Telegram!`
- Deve mostrar: `🕐 Bot iniciado às XX:XX:XX UTC`

### 2. Bot está ativado?
- Acesse: http://localhost:5000
- Verifique o painel "Controle do Bot"
- Deve estar em verde: "Bot Ativo"

### 3. Canal correto?
- Verifique se o `TELEGRAM_CHANNEL` no `.env` está correto
- O bot deve mostrar: `✅ Grupo encontrado: [nome] (ID: [id])`

## ❌ Problemas Comuns

### Problema 1: Mensagem muito antiga
**Sintoma:** Bot mostra `⏭️ Mensagem antiga ignorada`

**Causa:** O bot ignora mensagens enviadas ANTES dele iniciar

**Solução:** 
- Envie uma NOVA mensagem DEPOIS que o bot iniciar
- Ou reinicie o bot e envie a mensagem imediatamente

### Problema 2: Mensagem não está no formato correto
**Sintoma:** Bot não detecta nada

**Formato esperado:**
```
#SYMBOL ● $0.0₃62 62K FDV atualmente

Score: 15 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 3pts)

CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump
```

**Elementos obrigatórios:**
- ✅ `#SYMBOL` (símbolo do token)
- ✅ `$0.0₃62` (preço)
- ✅ `Score: 15` (score)
- ✅ `CA: [endereço]` (contract address)

### Problema 3: Bot não tem permissão
**Sintoma:** Bot conecta mas não recebe mensagens

**Solução:**
- Certifique-se que o bot está adicionado ao canal/grupo
- Se for grupo privado, adicione o bot como membro
- Verifique se o bot tem permissão para ler mensagens

### Problema 4: Canal errado
**Sintoma:** Bot não encontra o canal

**Solução:**
- Verifique o nome do canal no `.env`
- Ou use o ID do canal (número negativo)
- Execute: `python descobrir_grupo.py` para ver todos os grupos

## 🧪 Teste Manual

1. **Pare o bot** (Ctrl+C)

2. **Execute o teste:**
```bash
python testar_telegram.py
```

3. **Envie uma mensagem no formato correto**

4. **Veja se o bot detecta**

## 📋 Checklist

- [ ] Bot está rodando?
- [ ] Bot está ativado na interface?
- [ ] Canal está correto no `.env`?
- [ ] Mensagem foi enviada DEPOIS que o bot iniciou?
- [ ] Mensagem está no formato correto?
- [ ] Bot tem permissão no canal/grupo?
- [ ] Não há outro processo usando a sessão do Telegram?

## 💡 Dica

Se nada funcionar, verifique os logs do bot no terminal. Ele deve mostrar:
- `📨 Mensagem recebida` quando recebe uma mensagem
- `⚠️ Parse falhou` se a mensagem não está no formato correto
- `⏭️ Mensagem antiga ignorada` se a mensagem é antiga










