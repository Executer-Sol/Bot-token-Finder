# 🔄 Substituir APIs Externas por Alchemy Data APIs

**Objetivo:** Usar **APENAS** APIs do Alchemy, eliminando dependências externas (Jupiter, etc.)

**Documentação:** https://www.alchemy.com/docs/data

---

## 📊 Análise: O Que Estamos Usando Atualmente

### ❌ **APIs Externas que DEVEM ser substituídas:**

1. **Jupiter Price API** → Substituir por **Alchemy Prices API**
2. **Jupiter Quote API** → Manter (necessário para swaps)
3. **Jupiter Swap API** → Manter (necessário para executar swaps)
4. **Polling manual** → Substituir por **Alchemy Webhooks**

---

## ✅ Substituições Recomendadas

### 1. **Jupiter Price API → Alchemy Prices API** ⭐⭐⭐⭐⭐
**Prioridade: ALTA - IMPLEMENTAR PRIMEIRO**

**O que substituir:**
```python
# ATUAL (price_monitor.py):
- get_token_price_jupiter() → ❌ Remover
- get_token_price_birdeye() → ❌ Remover (opcional)

# NOVO (usar Alchemy):
- get_token_price_alchemy() → ✅ Usar Prices API
```

**Endpoints Alchemy:**
- `GET /v0/token-prices/{token_address}` - Preço atual
- `GET /v0/token-prices/historical` - Preço histórico
- `GET /v0/token-prices/by-symbol` - Preço por símbolo

**Benefícios:**
- ✅ **Já está pagando** pela API Alchemy
- ✅ **Mais rápido** (menos latência)
- ✅ **Mais confiável** (dados diretos)
- ✅ **Multi-chain** (Ethereum, Base, Polygon, etc.)
- ✅ **Histórico de preços** incluído

**Arquivos a modificar:**
- `price_monitor.py` - Adicionar método Alchemy
- `alchemy_integration.py` - Implementar Prices API
- `take_profit.py` - Usar Alchemy ao invés de Jupiter
- `bot.py` - Usar Alchemy para preços

---

### 2. **Token Metadata (Manual) → Alchemy Token API** ⭐⭐⭐⭐
**Prioridade: ALTA**

**O que substituir:**
```python
# ATUAL:
- Buscar metadados manualmente via Jupiter Token List
- Buscar logo, nome, símbolo de múltiplas fontes

# NOVO:
- alchemy_getTokenMetadata() → ✅ Token API
```

**Endpoints Alchemy:**
- `alchemy_getTokenMetadata` - Metadados completos
- `alchemy_getTokenBalances` - Saldos de tokens
- `alchemy_getTokenAllowance` - Allowances

**Benefícios:**
- ✅ **Dados completos** em uma chamada
- ✅ **Multi-chain** suportado
- ✅ **Mais rápido** que buscar múltiplas fontes
- ✅ **Sempre atualizado**

**Arquivos a modificar:**
- `wallet_tokens.py` - Usar Token API
- `alchemy_integration.py` - Adicionar métodos Token API

---

### 3. **Polling Manual → Alchemy Webhooks** ⭐⭐⭐⭐⭐
**Prioridade: ALTA - MAIOR IMPACTO**

**O que substituir:**
```python
# ATUAL (polling a cada 3-5 segundos):
- setInterval(() => loadData(), 3000) → ❌ Remover
- monitor_transactions() com sleep → ❌ Remover

# NOVO:
- Webhook Address Activity → ✅ Receber eventos automaticamente
- Webhook Custom → ✅ Filtrar eventos específicos
```

**Webhooks Alchemy:**
- **Address Activity Webhook** - Transferências de valor e tokens
- **Custom Webhook** - Eventos personalizados (swaps, vendas, etc.)

**Benefícios:**
- ✅ **Instantâneo** (sem delay de polling)
- ✅ **80% menos requisições** (economia de custos)
- ✅ **Mais confiável** (não perde eventos)
- ✅ **Escalável** (funciona com múltiplas carteiras)

**Arquivos a modificar:**
- `alchemy_realtime_monitor.py` - Substituir por Webhooks
- `web_interface.py` - Adicionar endpoint para receber webhooks
- `templates/dashboard.html` - Remover polling, usar eventos

---

### 4. **Transfers Manual → Alchemy Transfers API** ⭐⭐⭐⭐
**Prioridade: MÉDIA-ALTA**

**O que substituir:**
```python
# ATUAL:
- get_wallet_transactions_solscan() → ❌ Remover
- get_transaction_details_from_solana_rpc() → ⚠️ Manter como fallback

# NOVO:
- alchemy_getAssetTransfers() → ✅ Transfers API
```

**Endpoints Alchemy:**
- `alchemy_getAssetTransfers` - Histórico completo de transferências
- Filtros: por token, por tipo, por data, etc.

**Benefícios:**
- ✅ **Uma chamada** para todo o histórico
- ✅ **Filtros avançados** (por token, tipo, data)
- ✅ **Multi-chain** (Ethereum, Polygon, etc.)
- ✅ **Mais rápido** que buscar múltiplas fontes

**Arquivos a modificar:**
- `update_sell_prices.py` - Usar Transfers API
- `alchemy_integration.py` - Adicionar método getAssetTransfers

---

### 5. **Portfolio Manual → Alchemy Portfolio API** ⭐⭐⭐
**Prioridade: MÉDIA (já está parcialmente implementado)**

**O que melhorar:**
```python
# ATUAL (já usa Portfolio API parcialmente):
- get_portfolio() → ✅ Já implementado
- ⚠️ Não usa todos os endpoints disponíveis

# MELHORAR:
- getTokensByAddress() → ✅ Adicionar
- getTokenBalancesByAddress() → ✅ Adicionar
- getNFTsByAddress() → ✅ Adicionar (futuro)
```

**Endpoints Alchemy:**
- `GET /v0/accounts/{address}/tokens` - Tokens por carteira
- `GET /v0/accounts/{address}/token-balances` - Saldos de tokens
- `GET /v0/accounts/{address}/nfts` - NFTs por carteira

**Benefícios:**
- ✅ **Dados mais completos**
- ✅ **Menos chamadas** (tudo em uma)
- ✅ **Multi-chain** suportado

**Arquivos a modificar:**
- `alchemy_integration.py` - Melhorar get_portfolio()
- `wallet_balance.py` - Usar Portfolio API completo

---

## 🚫 O Que NÃO Substituir (Manter)

### **Jupiter Swap API** ⚠️
**Por que manter:**
- Alchemy **não tem** Swap API para Solana
- Jupiter é o **melhor aggregator** para Solana
- **Necessário** para executar compras/vendas

**O que fazer:**
- ✅ Manter Jupiter para **executar swaps**
- ✅ Usar Alchemy para **tudo mais** (preços, metadados, webhooks)

---

## 📋 Plano de Implementação

### **Fase 1 - Substituir Preços (Semana 1)**
1. ✅ Implementar **Alchemy Prices API** em `alchemy_integration.py`
2. ✅ Modificar `price_monitor.py` para usar Alchemy primeiro
3. ✅ Atualizar `take_profit.py` para usar Alchemy
4. ✅ Testar e validar preços

**Resultado:** Preços vêm direto do Alchemy (mais rápido, mais confiável)

---

### **Fase 2 - Substituir Polling por Webhooks (Semana 1-2)**
1. ✅ Configurar **Webhook Address Activity** no dashboard Alchemy
2. ✅ Criar endpoint Flask `/api/alchemy/webhook` para receber eventos
3. ✅ Processar eventos e atualizar interface automaticamente
4. ✅ Remover polling do frontend

**Resultado:** Atualizações instantâneas, 80% menos requisições

---

### **Fase 3 - Melhorar Token API (Semana 2)**
1. ✅ Implementar `alchemy_getTokenMetadata()` em `alchemy_integration.py`
2. ✅ Substituir busca manual de metadados
3. ✅ Usar Token API em `wallet_tokens.py`

**Resultado:** Metadados completos em uma chamada

---

### **Fase 4 - Melhorar Transfers API (Semana 2-3)**
1. ✅ Implementar `alchemy_getAssetTransfers()` completo
2. ✅ Substituir Solscan por Alchemy Transfers API
3. ✅ Adicionar filtros avançados

**Resultado:** Histórico completo e filtrado

---

## 📊 Comparação: Antes vs Depois

| Funcionalidade | Antes (APIs Externas) | Depois (Alchemy Only) |
|----------------|----------------------|------------------------|
| **Preços de Tokens** | Jupiter Price API | ✅ Alchemy Prices API |
| **Metadados de Tokens** | Jupiter Token List + Manual | ✅ Alchemy Token API |
| **Histórico de Transações** | Solscan + RPC | ✅ Alchemy Transfers API |
| **Atualizações em Tempo Real** | Polling (3-5s) | ✅ Alchemy Webhooks (< 1s) |
| **Portfólio** | Múltiplas fontes | ✅ Alchemy Portfolio API |
| **Swaps (Execução)** | Jupiter Swap API | ⚠️ Manter Jupiter (Alchemy não tem) |

---

## 💰 Economia de Custos

### **Antes:**
- Polling a cada 3s = **1.200 requisições/hora**
- Múltiplas APIs (Jupiter, Solscan, etc.)
- **Custo alto** em requisições

### **Depois:**
- Webhooks = **~10-50 eventos/hora** (apenas quando há mudanças)
- Uma API (Alchemy) para tudo
- **80-90% menos requisições**

**Economia estimada:** 80-90% menos custos de API

---

## 🎯 Resumo Executivo

### **O Que Fazer:**
1. ✅ **Substituir Jupiter Price API** → Alchemy Prices API
2. ✅ **Substituir Polling** → Alchemy Webhooks
3. ✅ **Substituir Solscan** → Alchemy Transfers API
4. ✅ **Melhorar Token Metadata** → Alchemy Token API
5. ✅ **Melhorar Portfolio** → Alchemy Portfolio API completo

### **O Que Manter:**
- ⚠️ **Jupiter Swap API** (Alchemy não tem para Solana)

### **Resultado Final:**
- ✅ **100% Alchemy** para dados (preços, metadados, histórico)
- ✅ **Jupiter apenas** para executar swaps
- ✅ **80% menos requisições** (webhooks vs polling)
- ✅ **Mais rápido** (dados diretos do Alchemy)
- ✅ **Mais confiável** (uma fonte de verdade)

---

## 📚 Referências

- [Alchemy Data APIs Overview](https://www.alchemy.com/docs/data)
- [Prices API Quickstart](https://www.alchemy.com/docs/reference/prices-api-quickstart)
- [Token API Overview](https://www.alchemy.com/docs/reference/token-api-overview)
- [Transfers API Overview](https://www.alchemy.com/docs/reference/transfers-api-quickstart)
- [Webhooks Overview](https://www.alchemy.com/docs/reference/webhooks-overview)
- [Portfolio API Overview](https://www.alchemy.com/docs/reference/portfolio-apis)










