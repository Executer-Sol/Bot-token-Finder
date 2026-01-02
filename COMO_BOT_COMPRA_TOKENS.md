# 🔄 Sistema Completo: Como o Bot Compra Tokens

## 🎯 Fluxo Completo Passo a Passo

### 1. **DETECÇÃO NO TELEGRAM** 📱

```
Mensagem chega no canal → Bot detecta → Faz parse automático
```

**Exemplo de mensagem no Telegram:**
```
#oddbit ● $0.0₃62 62K FDV atualmente

Score: 15 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 3pts)

2 wallets com 1k-3k em compras nos últimos minutos.

Detectado há 6 minutos pela primeira vez nos 20K FDV.

CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump
```

**O que o bot extrai:**
- ✅ Símbolo: `oddbit`
- ✅ Preço: `$0.000062`
- ✅ Score: `15`
- ✅ **Contract Address (CA):** `A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump` ← **ESSENCIAL!**
- ✅ Tempo: `6 minutos`

---

### 2. **VALIDAÇÕES** ✅

Antes de comprar, o bot verifica:

#### 2.1. Bot está ativado?
```python
if not get_bot_state():
    return  # Não compra se bot desativado
```

#### 2.2. Token não está na blacklist?
```python
if is_blacklisted(token_info.contract_address):
    return  # Não compra tokens bloqueados
```

#### 2.3. Score válido?
```python
if score < 15 or score > 21:
    return  # Fora do range
```

#### 2.4. Dentro da janela de tempo?
```python
# Score 15-17: máximo 3 minutos
# Score 18-19: máximo 5 minutos
# Score 20-21: máximo 1 minuto
if minutes_detected > max_time:
    return  # Muito tarde
```

#### 2.5. Tem SOL suficiente?
```python
balance = await get_wallet_balance()
if balance['sol'] < amount_sol + 0.01:  # +0.01 para taxas
    return  # Saldo insuficiente
```

#### 2.6. Token já foi comprado?
```python
if contract_address in self.active_trades:
    return  # Já está negociando este token
```

---

### 3. **CÁLCULO DO VALOR** 💰

Baseado no score do token:

```python
# Score 15-17 → 0.05 SOL (~$5)
# Score 18-19 → 0.03 SOL (~$3)
# Score 20-21 → 0.02 SOL (~$2)

amount_sol = config.get_amount_by_score(score)
```

**Exemplo:**
- Token com Score 15 → Investe **0.05 SOL**
- Token com Score 18 → Investe **0.03 SOL**

---

### 4. **COMPRA VIA JUPITER API** 🚀

#### 4.1. Obtém Quote (Cotação)

```python
# Chama Jupiter API
GET https://quote-api.jup.ag/v6/quote
Params:
  - inputMint: "So11111111111111111111111111111111111111112" (SOL)
  - outputMint: "A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump" (Token)
  - amount: 50000000 (0.05 SOL em lamports)
  - slippageBps: 500 (5% slippage)
```

**Resposta da API:**
```json
{
  "outAmount": "1000000000",  // Quantidade de tokens que receberá
  "priceImpactPct": "0.01",
  "route": [...]
}
```

#### 4.2. Prepara Transação

```python
# Chama Jupiter API para gerar transação
POST https://quote-api.jup.ag/v6/swap
Body: {
  "quoteResponse": {quote},
  "userPublicKey": "sua_carteira_publica",
  "wrapUnwrapSOL": true,
  "dynamicComputeUnitLimit": true
}
```

**Resposta:**
```json
{
  "swapTransaction": "base64_encoded_transaction"
}
```

#### 4.3. Assina e Envia para Blockchain

```python
# Decodifica transação
transaction_bytes = base64.b64decode(swap_transaction)
transaction = VersionedTransaction.from_bytes(transaction_bytes)

# Assina com sua chave privada
transaction.sign([keypair])

# Envia para Solana
tx_signature = await client.send_transaction(transaction)
# Retorna: "5j2h1g9f8e7d6c5b4a3k2j1h9g8f7e6d5c4b3a2k1j9h8g7f6e5d4c3b2a1k"
```

---

### 5. **PÓS-COMPRA** 📊

Após comprar, o bot:

1. **Salva no histórico:**
   ```python
   log_trade_bought(
       symbol="oddbit",
       contract_address="A6RTAd...",
       entry_price=0.000062,
       amount_sol=0.05,
       score=15,
       tx_signature="5j2h1g9f..."
   )
   ```

2. **Inicia monitoramento:**
   ```python
   tp_manager.add_position(
       contract_address="A6RTAd...",
       symbol="oddbit",
       amount_tokens=1000000000,
       entry_price=0.000062,
       score=15
   )
   ```

3. **Monitora preço:**
   - Verifica preço a cada 10 segundos
   - Quando atinge take profit (2x, 4x, 8x) → vende parcialmente
   - Continua monitorando até vender tudo

---

## 📋 Resumo Visual do Fluxo

```
┌─────────────────────────────────────────────────────────┐
│  1. TELEGRAM                                           │
│     Mensagem chega no canal                            │
│     #oddbit | Score: 15 | CA: A6RTAd...               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  2. PARSE & VALIDAÇÃO                                  │
│     ✅ Extrai CA, Score, Preço                        │
│     ✅ Bot ativado?                                   │
│     ✅ Score válido?                                  │
│     ✅ Dentro da janela de tempo?                     │
│     ✅ Tem SOL suficiente?                            │
│     ✅ Não está na blacklist?                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  3. CALCULA VALOR                                      │
│     Score 15 → 0.05 SOL                               │
│     Score 18 → 0.03 SOL                               │
│     Score 20 → 0.02 SOL                               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  4. JUPITER API - QUOTE                                │
│     GET /v6/quote                                      │
│     SOL → Token                                        │
│     Retorna: quantidade de tokens                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  5. JUPITER API - SWAP                                 │
│     POST /v6/swap                                      │
│     Gera transação assinada                            │
│     Retorna: transaction (base64)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  6. SOLANA BLOCKCHAIN                                  │
│     Assina transação com sua chave privada             │
│     Envia para rede Solana                             │
│     Retorna: TX Hash                                   │
│     Exemplo: 5j2h1g9f8e7d6c5b4a3...                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  7. CONFIRMADO! ✅                                     │
│     Token comprado!                                    │
│     TX: solscan.io/tx/5j2h1g9f...                     │
│     Inicia monitoramento de preço                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Componentes Principais

### **1. message_parser.py**
- Faz parse da mensagem do Telegram
- Extrai: símbolo, preço, score, **CA**, tempo
- **CA é essencial** - sem ela, não compra!

### **2. jupiter_client.py**
- Cliente da Jupiter API
- Métodos:
  - `get_quote()` - Obtém cotação
  - `swap()` - Gera transação
  - `buy_token()` - Compra completa (quote + swap + envio)
  - `send_transaction()` - Envia para blockchain

### **3. bot.py**
- Orquestra todo o processo
- Valida tudo antes de comprar
- Chama `jupiter.buy_token(CA, amount_sol)`

---

## 💻 Código Principal

### **Bot detecta token:**
```python
# bot.py - on_new_message()
token_info = parse_token_message(message)
# token_info.contract_address = "A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump"

# Validações...

# Compra!
tx_signature, quote = await self.jupiter.buy_token(
    token_info.contract_address,  # ← CA do token
    amount_sol                     # ← Quantidade em SOL
)
```

### **Jupiter executa compra:**
```python
# jupiter_client.py - buy_token()
# 1. Obtém quote: SOL → Token
quote = await self.get_quote(SOL_MINT, token_address, amount_lamports)

# 2. Gera transação
swap_transaction = await self.swap(quote, use_sol=True)

# 3. Assina e envia
transaction_bytes = base64.b64decode(swap_transaction)
transaction = VersionedTransaction.from_bytes(transaction_bytes)
transaction.sign([self.keypair])  # ← Sua chave privada
tx_signature = await self.client.send_transaction(transaction)

return tx_signature, quote
```

---

## 🎯 Pontos Importantes

### **1. A CA é essencial!**
- Sem a CA (Contract Address), o bot **não pode comprar**
- A CA identifica o token na blockchain Solana
- O bot extrai a CA automaticamente do Telegram

### **2. Usa sua chave privada**
- Chave privada vem do `.env` (`SOLANA_PRIVATE_KEY`)
- Bot assina transações com sua carteira
- **Você precisa ter SOL na carteira!**

### **3. Tudo é automático**
- Bot detecta → Valida → Compra → Monitora
- Você só precisa manter o bot rodando

### **4. Jupiter API é intermediária**
- Não compra diretamente na blockchain
- Usa Jupiter para encontrar melhor rota
- Jupiter encontra DEX com melhor preço (Raydium, Orca, etc.)

---

## 📊 Exemplo Real Completo

### **Mensagem no Telegram:**
```
#oddbit ● $0.0₃62 62K FDV
Score: 15
CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump
Detectado há 2 minutos
```

### **Processo:**
1. ✅ Bot detecta e extrai CA
2. ✅ Score 15 → Valida (dentro do range)
3. ✅ 2 minutos < 3 minutos → Valida (dentro da janela)
4. ✅ Bot ativado → Valida
5. ✅ Tem SOL → Valida (0.2 SOL > 0.05 SOL)
6. ✅ Calcula: Score 15 → 0.05 SOL
7. ✅ Chama Jupiter: `buy_token("A6RTAd...", 0.05)`
8. ✅ Jupiter obtém quote: 0.05 SOL → 1.000.000 tokens oddbit
9. ✅ Jupiter gera transação
10. ✅ Bot assina com sua chave
11. ✅ Envia para Solana
12. ✅ **Compra realizada! TX: 5j2h1g9f...**
13. ✅ Salva no histórico
14. ✅ Inicia monitoramento

---

## 🔒 Segurança

### **Sua chave privada:**
- Fica no `.env` (nunca compartilhada)
- Bot usa apenas para assinar transações
- Você controla totalmente a carteira

### **Validações protegem:**
- Não compra tokens ruins (blacklist)
- Não compra fora da janela (timing)
- Não compra sem SOL (saldo)
- Não compra mesmo token duas vezes

---

## 📝 Resumo em 3 Linhas

1. **Bot lê mensagem do Telegram** → Extrai CA automaticamente
2. **Valida tudo** (score, tempo, saldo, blacklist)
3. **Compra via Jupiter API** usando sua chave privada → Token comprado!

**Tudo automático! Você só mantém o bot rodando.** 🚀











