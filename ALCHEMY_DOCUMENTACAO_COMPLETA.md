# 📚 Documentação Completa do Alchemy para Solana

Baseado em: [https://www.alchemy.com/docs/get-started](https://www.alchemy.com/docs/get-started)

---

## 🎯 Visão Geral

A Alchemy oferece uma plataforma completa para desenvolvedores Web3, fornecendo infraestrutura confiável para interagir com blockchains. Para Solana, as principais APIs disponíveis são:

---

## 1. 📡 Node API (JSON-RPC)

### **O que é:**
Acesso de baixo nível aos métodos JSON-RPC padrão para interagir com a blockchain Solana.

### **Métodos Principais para Solana:**

#### **1.1. Consultas de Conta**
- `getBalance(address)` - Saldo SOL de uma conta
- `getAccountInfo(address)` - Informações completas da conta
- `getTokenAccountsByOwner(owner, mint)` - Contas de tokens SPL
- `getTokenAccountBalance(address)` - Saldo de um token específico

#### **1.2. Transações**
- `getTransaction(signature)` - Detalhes completos de uma transação
- `getTransactionStatus(signature)` - Status de uma transação
- `getSignaturesForAddress(address, limit)` - Histórico de transações
- `sendTransaction(transaction)` - Enviar transação

#### **1.3. Blocos e Slots**
- `getSlot()` - Slot atual da rede
- `getBlockHeight()` - Altura do bloco atual
- `getBlock(slot)` - Dados de um bloco específico
- `getBlockTime(slot)` - Timestamp de um slot

#### **1.4. Programas e Logs**
- `getProgramAccounts(programId)` - Contas de um programa
- `getLogs(filter)` - Logs de transações/programas

### **Exemplo de Uso:**
```python
from solana.rpc.async_api import AsyncClient

client = AsyncClient("https://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY")

# Buscar saldo
balance = await client.get_balance(wallet_address)
sol_amount = balance.value / 1e9

# Buscar transações
signatures = await client.get_signatures_for_address(
    wallet_address,
    limit=10
)

# Buscar detalhes de transação
tx = await client.get_transaction(
    signature,
    encoding="jsonParsed"
)
```

---

## 2. 📊 Data APIs (Dados Estruturados)

### **O que é:**
Dados estruturados e indexados que seriam difíceis de obter apenas via RPC. Otimizadas para leituras de alto volume.

### **2.1. Portfolio API**
**Endpoint:** `GET /v0/accounts/{address}/portfolio`

**O que oferece:**
- Visão completa do portfólio de uma carteira
- Todos os tokens SPL com valores em USD
- NFTs na carteira
- Saldo SOL
- Valor total do portfólio

**Exemplo de Resposta:**
```json
{
  "sol_balance": 1.5,
  "tokens": [
    {
      "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "symbol": "USDC",
      "balance": 1000.0,
      "value_usd": 1000.0
    }
  ],
  "total_value_usd": 1225.0
}
```

### **2.2. Transfers API**
**Endpoint:** `GET /v0/accounts/{address}/transfers`

**O que oferece:**
- Histórico completo de transferências
- Transferências de SOL
- Transferências de tokens SPL
- Filtros por tipo, token, data
- Paginação

**Parâmetros:**
- `fromBlock` - Bloco inicial
- `toBlock` - Bloco final
- `category` - `external`, `internal`, `erc20`, `erc721`, `erc1155`
- `withMetadata` - Incluir metadados

**Exemplo de Uso:**
```python
import aiohttp

async def get_transfers(address):
    url = f"https://solana-mainnet.g.alchemy.com/v0/accounts/{address}/transfers"
    headers = {"X-Alchemy-Token": "YOUR_API_KEY"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data['transfers']
```

### **2.3. Prices API**
**Endpoint:** `GET /v0/prices/token/{tokenAddress}`

**O que oferece:**
- Preços de tokens em tempo real
- Preços históricos
- Múltiplos tokens em uma requisição
- Dados de mercado (volume, market cap)

**Exemplo:**
```python
# Preço de um token
url = "https://solana-mainnet.g.alchemy.com/v0/prices/token/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
# Retorna: {"price": 1.0, "currency": "USD", "timestamp": ...}
```

### **2.4. NFT API**
**Endpoint:** `GET /v0/accounts/{address}/nfts`

**O que oferece:**
- NFTs na carteira
- Metadados completos
- Imagens e atributos
- Coleções

---

## 3. 🔔 WebSockets (Tempo Real)

### **O que é:**
Subscrições em tempo real para eventos on-chain.

### **Eventos Disponíveis:**

#### **3.1. Pending Transactions**
```python
# Monitora transações pendentes
ws_url = "wss://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

# Subscribe
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "transactionSubscribe",
  "params": [
    {
      "vote": false,
      "accountInclude": [wallet_address]
    }
  ]
}
```

#### **3.2. Account Changes**
```python
# Monitora mudanças em contas
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "accountSubscribe",
  "params": [
    wallet_address,
    {
      "encoding": "jsonParsed"
    }
  ]
}
```

#### **3.3. Slot Updates**
```python
# Monitora novos slots
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "slotSubscribe"
}
```

### **Exemplo de Implementação:**
```python
import asyncio
import websockets
import json

async def monitor_wallet_realtime():
    uri = "wss://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
    
    async with websockets.connect(uri) as ws:
        # Subscribe a transações da carteira
        subscribe_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "transactionSubscribe",
            "params": [{
                "accountInclude": [wallet_address]
            }]
        }
        await ws.send(json.dumps(subscribe_msg))
        
        # Recebe eventos em tempo real
        async for message in ws:
            data = json.loads(message)
            if 'params' in data:
                # Nova transação detectada!
                process_transaction(data['params']['result'])
```

---

## 4. 🔍 Trace API (Análise de Transações)

### **O que é:**
Insights detalhados sobre processamento de transações e atividade on-chain.

### **Métodos:**
- `traceTransaction(signature)` - Rastreamento completo de uma transação
- `traceBlock(slot)` - Rastreamento de todas as transações em um bloco

### **O que oferece:**
- Caminho completo da transação
- Todas as chamadas de programas
- Mudanças de estado
- Gas usado (em Solana: compute units)

---

## 5. 🐛 Debug API

### **O que é:**
Métodos RPC não-padrão para inspecionar e debugar transações.

### **Métodos Úteis:**
- `simulateTransaction(transaction)` - Simular transação sem enviar
- `getTransactionLogs(signature)` - Logs detalhados
- `getAccountInfo(address)` - Informações de debug

---

## 6. ⚡ Yellowstone gRPC (Solana Específico)

### **O que é:**
Interface de streaming de dados Solana em tempo real de alta performance.

### **Recursos:**
- Streaming de slots
- Streaming de transações
- Streaming de contas
- Alta performance e baixa latência

---

## 7. 🔔 Webhooks (Notificações)

### **O que é:**
Notificações automáticas quando eventos específicos acontecem na blockchain.

### **Eventos Disponíveis:**
- **Transfers** - Transferências de SOL ou tokens
- **Transactions** - Novas transações
- **Balance Changes** - Mudanças de saldo
- **NFT Transfers** - Transferências de NFTs

### **Configuração:**
1. Criar webhook no Alchemy Dashboard
2. Configurar URL de callback
3. Selecionar eventos para monitorar
4. Receber notificações em tempo real

### **Exemplo de Payload:**
```json
{
  "webhook_id": "wh_abc123",
  "id": "evt_xyz789",
  "created_at": "2024-01-01T00:00:00Z",
  "type": "TRANSACTION",
  "event": {
    "network": "SOLANA_MAINNET",
    "transaction": {
      "signature": "...",
      "from": "...",
      "to": "...",
      "value": 0.5
    }
  }
}
```

---

## 🚀 APIs Mais Úteis para o Bot de Trading

### **Prioridade Alta:**

1. **Transfers API** ✅
   - Detectar vendas automaticamente
   - Histórico completo de transações
   - Identificar swaps (token → SOL)

2. **Portfolio API** ✅
   - Ver todos os tokens na carteira
   - Valores em USD
   - Atualização em tempo real

3. **WebSockets** ✅
   - Monitoramento em tempo real
   - Detectar novas transações instantaneamente
   - Sem polling constante

4. **Prices API** ✅
   - Preços de tokens em tempo real
   - Melhor que Jupiter para alguns casos
   - Dados históricos

### **Prioridade Média:**

5. **Trace API**
   - Análise detalhada de swaps
   - Entender exatamente o que aconteceu

6. **Webhooks**
   - Notificações automáticas
   - Reduz carga no servidor

### **Prioridade Baixa:**

7. **NFT API**
   - Se quiser rastrear NFTs também

8. **Debug API**
   - Para debugging avançado

---

## 📝 Exemplo Completo: Monitoramento em Tempo Real

```python
import asyncio
import aiohttp
from solana.rpc.async_api import AsyncClient

class AlchemyMonitor:
    def __init__(self, api_key, wallet_address):
        self.api_key = api_key
        self.wallet_address = wallet_address
        self.rpc_url = f"https://solana-mainnet.g.alchemy.com/v2/{api_key}"
        self.data_api_url = "https://solana-mainnet.g.alchemy.com/v0"
        self.client = AsyncClient(self.rpc_url)
    
    async def get_portfolio(self):
        """Busca portfólio completo via Data API"""
        url = f"{self.data_api_url}/accounts/{self.wallet_address}/portfolio"
        headers = {"X-Alchemy-Token": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
    
    async def get_recent_transfers(self, limit=50):
        """Busca transferências recentes"""
        url = f"{self.data_api_url}/accounts/{self.wallet_address}/transfers"
        headers = {"X-Alchemy-Token": self.api_key}
        params = {"limit": limit}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                return await response.json()
    
    async def get_token_price(self, token_address):
        """Busca preço de um token"""
        url = f"{self.data_api_url}/prices/token/{token_address}"
        headers = {"X-Alchemy-Token": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data.get('price', 0)
    
    async def monitor_transactions(self):
        """Monitora transações em tempo real via RPC"""
        last_signature = None
        
        while True:
            try:
                # Busca última transação
                signatures = await self.client.get_signatures_for_address(
                    self.wallet_address,
                    limit=1
                )
                
                if signatures.value and signatures.value[0].signature != last_signature:
                    # Nova transação!
                    tx_sig = signatures.value[0].signature
                    tx = await self.client.get_transaction(
                        tx_sig,
                        encoding="jsonParsed"
                    )
                    
                    # Processa transação
                    await self.process_transaction(tx.value)
                    
                    last_signature = tx_sig
                
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Erro: {e}")
                await asyncio.sleep(10)
    
    async def process_transaction(self, tx):
        """Processa uma transação e identifica vendas"""
        # Analisa se é uma venda (recebeu SOL)
        # Extrai informações do token vendido
        # Atualiza preços de venda
        pass
```

---

## 🔑 Como Obter API Key

1. Acesse: [https://dashboard.alchemy.com/signup](https://dashboard.alchemy.com/signup)
2. Crie uma conta gratuita
3. Crie um novo app (selecione Solana)
4. Copie a API Key
5. Use no código: `https://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY`

---

## 📊 Comparação: RPC vs Data APIs

| Recurso | RPC (Node API) | Data APIs |
|---------|----------------|-----------|
| **Saldos** | ✅ Básico | ✅ Completo com USD |
| **Transações** | ✅ Básico | ✅ Enriquecido |
| **Histórico** | ⚠️ Limitado | ✅ Completo |
| **Preços** | ❌ Não | ✅ Sim |
| **Performance** | ⚠️ Média | ✅ Alta |
| **Filtros** | ⚠️ Básico | ✅ Avançado |

**Recomendação:** Use **Data APIs** para leitura e **RPC** para escrita (transações).

---

## 🎯 Implementações Recomendadas para o Bot

### **1. Usar Transfers API para Detectar Vendas**
```python
# Mais eficiente que buscar todas as transações
transfers = await get_recent_transfers(limit=100)
sells = [t for t in transfers if t['to'] == wallet_address and t['category'] == 'external']
```

### **2. Usar Portfolio API para Dashboard**
```python
# Uma requisição = todos os dados
portfolio = await get_portfolio()
# Retorna: SOL, tokens, valores USD, tudo pronto!
```

### **3. Usar WebSockets para Tempo Real**
```python
# Sem polling, recebe eventos instantaneamente
# Reduz carga no servidor
# Mais eficiente
```

### **4. Usar Prices API para Preços**
```python
# Mais confiável que Jupiter em alguns casos
# Dados históricos disponíveis
# Múltiplos tokens de uma vez
```

---

## 📚 Links Úteis

- **Documentação Principal:** [https://www.alchemy.com/docs/get-started](https://www.alchemy.com/docs/get-started)
- **Node API:** [https://www.alchemy.com/docs/reference/node-api-overview](https://www.alchemy.com/docs/reference/node-api-overview)
- **Data APIs:** [https://www.alchemy.com/docs/reference/data-overview](https://www.alchemy.com/docs/reference/data-overview)
- **WebSockets:** [https://www.alchemy.com/docs/reference/subscription-api](https://www.alchemy.com/docs/reference/subscription-api)
- **Dashboard:** [https://dashboard.alchemy.com](https://dashboard.alchemy.com)

---

## 💡 Próximos Passos

**Quer que eu implemente alguma dessas APIs no bot?**

1. ✅ **Transfers API** - Detectar vendas automaticamente
2. ✅ **Portfolio API** - Dashboard completo
3. ✅ **WebSockets** - Monitoramento em tempo real
4. ✅ **Prices API** - Preços mais precisos

Qual você quer implementar primeiro? 🚀










