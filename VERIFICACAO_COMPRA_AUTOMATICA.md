# ✅ Compra Automática - Já Está Funcionando!

## 🎯 O Bot Já Compra Automaticamente!

Quando você vê uma mensagem no Telegram como:

```
#oddbit ● $0.0₃62 62K FDV atualmente
Score: 15 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 3pts)
Detectado há 6 minutos pela primeira vez nos 20K FDV.
CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump
```

**O bot faz automaticamente:**
1. ✅ Lê a mensagem do Telegram
2. ✅ Extrai a CA (Contract Address): `A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump`
3. ✅ Extrai o Score: `15`
4. ✅ Valida se deve comprar (score, tempo, etc)
5. ✅ **COMPRA AUTOMATICAMENTE** usando sua carteira Jupiter (chave privada do .env)

---

## ⚙️ Como Funciona

### 1. **Detecção no Telegram**
- Bot monitora o canal configurado
- Quando aparece mensagem com token, faz parse automático

### 2. **Validação Automática**
- Score entre 15-21? ✅
- Dentro da janela de tempo? ✅
- Bot está ativado? ✅
- Tem SOL suficiente? ✅

### 3. **Compra Automática**
- Usa sua chave privada do `.env`
- Compra via Jupiter API
- Valor baseado no score:
  - Score 15-17: 0.05 SOL
  - Score 18-19: 0.03 SOL
  - Score 20-21: 0.02 SOL

### 4. **Monitoramento Automático**
- Após comprar, monitora preço
- Executa take profits automaticamente
- Vende em etapas (2x, 4x, 8x, etc)

---

## 🔍 Como Verificar se Está Funcionando

### 1. **Bot Está Rodando?**
```bash
python bot.py
```

Deve aparecer:
```
✅ Bot conectado ao Telegram!
👂 Monitorando canal: [nome do canal]
🤖 Bot ativo! Aguardando novos tokens...
```

### 2. **Bot Está Ativado?**
- Acesse: http://localhost:5000
- Verifique se mostra: "✅ Bot ATIVO"
- Se estiver desativado, clique em "▶️ Ativar Bot"

### 3. **Tem SOL na Carteira?**
- Verifique o saldo na interface web
- Precisa ter SOL suficiente para as compras

### 4. **O Que Aparece Quando Compra?**
Quando detectar e comprar um token, você verá no terminal:

```
🚀 Novo token detectado!
   Símbolo: oddbit
   Score: 15
   Preço: $0.000062
   CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump
   ⏱️  Tempo desde detecção: 2 minutos
   💰 Investindo: 0.05 SOL (baseado no score)
✅ Compra realizada! TX: [hash da transação]
📊 Posição monitorada: oddbit @ $0.000062
```

---

## ⚠️ Possíveis Problemas

### Bot Não Está Comprando?

1. **Bot desativado?**
   - Interface web: http://localhost:5000
   - Clique em "▶️ Ativar Bot"

2. **Score fora do range?**
   - Score deve estar entre 15-21
   - Score < 15: só compra se `ENABLE_LOW_SCORE=true` no .env

3. **Fora da janela de tempo?**
   - Score 15-17: máximo 3 minutos
   - Score 18-19: máximo 5 minutos
   - Score 20-21: máximo 1 minuto

4. **Sem SOL suficiente?**
   - Verifique saldo na interface web
   - Precisa ter SOL para pagar as taxas também

5. **Problema de DNS?**
   - Se aparecer erro de conexão com Jupiter API
   - Verifique: `SOLUCAO_DNS.md`

---

## 📋 Resumo

**✅ SIM, o bot JÁ compra automaticamente!**

- Usa sua chave privada do `.env`
- Compra via Jupiter API
- Tudo automático quando detecta token no Telegram
- Você só precisa manter o bot rodando e ativado

**Não precisa fazer nada manual!** O bot faz tudo sozinho quando vê a CA no Telegram. 🚀











