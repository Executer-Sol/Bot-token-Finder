# Mudança: Bot Agora Usa SOL em vez de USDC

## ✅ O que foi alterado:

### 1. **jupiter_client.py**
- Recriado para usar SOL
- `buy_token()` agora recebe `amount_sol` (em SOL, não lamports)
- `sell_token()` vende tokens de volta para SOL
- Usa `use_sol=True` para wrap/unwrap SOL automaticamente

### 2. **config.py**
- Mudou de `AMOUNT_USDC_*` para `AMOUNT_SOL_*`
- Valores padrão:
  - Score 15-17: 0.05 SOL (~$5 USD)
  - Score 18-19: 0.03 SOL (~$3 USD)
  - Score 20-21: 0.02 SOL (~$2 USD)
  - Score <15: 0.01 SOL (~$1 USD)

### 3. **bot.py**
- Agora usa `amount_sol` em vez de `amount_usdc`
- Mensagens atualizadas para mostrar SOL

### 4. **teste_solana_simples.py**
- Atualizado para usar SOL

## 📋 Configuração no .env

Agora você precisa configurar valores em SOL:

```env
# Valores por Score (em SOL)
AMOUNT_SOL_15_17=0.05    # Score 15-17: 0.05 SOL
AMOUNT_SOL_18_19=0.03    # Score 18-19: 0.03 SOL
AMOUNT_SOL_20_21=0.02    # Score 20-21: 0.02 SOL
AMOUNT_SOL_LOW=0.01      # Score <15: 0.01 SOL
```

## 💰 O que você precisa agora:

1. **SOL na carteira** (não precisa mais de USDC)
   - Para comprar tokens
   - Para pagar taxas de transação

2. **Exemplo de saldo mínimo:**
   - 0.5 SOL = suficiente para vários trades
   - 0.1 SOL = mínimo para testar

## ⚠️ Importante:

- O bot agora compra tokens com **SOL**
- Vende tokens de volta para **SOL**
- Não precisa mais de USDC na carteira
- Todas as configurações agora são em SOL

## 🔄 Diferenças:

| Antes (USDC) | Agora (SOL) |
|--------------|-------------|
| Precisava USDC | Precisa SOL |
| Valores fixos em $ | Valores fixos em SOL |
| 1 USDC = $1 | 1 SOL = ~$100 (varia) |











