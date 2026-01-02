# 📖 Resumo: Como o Bot de Trading Funciona

## 🎯 Visão Geral

O bot monitora automaticamente um canal/grupo do Telegram em busca de mensagens sobre novos tokens Solana. Quando detecta um token promissor (baseado em score), compra automaticamente usando SOL via Jupiter API e monitora o preço para executar vendas parciais (take profits) quando atinge múltiplos pré-configurados.

---

## 🔄 Fluxo Completo de Operação

### 1. **INICIALIZAÇÃO**
```
Bot inicia → Conecta ao Telegram → Busca canal/grupo configurado → Começa a monitorar mensagens
```

### 2. **DETECÇÃO DE TOKEN**
Quando uma nova mensagem chega no canal:
- O bot faz parse da mensagem para extrair:
  - Símbolo do token (ex: BONK, SHIRLEY)
  - Preço atual
  - Score (15-21)
  - Contract Address (CA)
  - Tempo desde detecção (minutos)

**Exemplo de mensagem parseada:**
```
#SHIRLEY ● $0.0₃82 82K FDV atualmente
Score: 16 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 4pts)
Detectado há 5 minutos pela primeira vez nos 61K FDV.
CA: FipAgs4hHCm5HBrD4rvAP8LGgrm1iWW4qgB1aTAYpump
```

### 3. **VALIDAÇÕES ANTES DE COMPRAR**

O bot verifica se deve comprar o token:

✅ **Estado do Bot**: Bot está ativado? (pode ser desativado via interface web)

✅ **Score dentro do range**: Score entre `MIN_SCORE` e `MAX_SCORE` (padrão: 15-21)

✅ **Valor configurado**: O score tem um valor em SOL configurado?

✅ **Janela de tempo**: Token foi detectado dentro do tempo máximo permitido?
- Score 15-17: máximo 3 minutos
- Score 18-19: máximo 5 minutos  
- Score 20-21: máximo 1 minuto (só imediato)

✅ **Token já comprado**: Não está comprando o mesmo token novamente

### 4. **COMPRA DO TOKEN**

Se passou em todas as validações:

**Processo:**
1. Calcula valor em SOL baseado no score:
   - Score 15-17: 0.05 SOL (~$5 USD)
   - Score 18-19: 0.03 SOL (~$3 USD)
   - Score 20-21: 0.02 SOL (~$2 USD)
   - Score <15: 0.01 SOL (~$1 USD) - se habilitado

2. Executa swap via Jupiter API:
   ```
   SOL → Token
   Exemplo: 0.05 SOL → 1.000.000 tokens BONK
   ```

3. Salva informações da compra:
   - Preço de entrada
   - Quantidade de tokens
   - Transaction hash (TX)
   - Score

4. Inicia monitoramento automático de preço

### 5. **MONITORAMENTO E TAKE PROFIT**

Após a compra, o bot inicia um loop que roda **a cada 10 segundos**:

**Para cada token comprado:**

1. **Busca preço atual** via múltiplas fontes (com fallback):
   - BirdEye API (se tiver API key)
   - Jupiter Price API
   - DexScreener API

2. **Calcula múltiplo e % de alta**:
   ```
   Múltiplo = Preço Atual / Preço de Entrada
   % Alta = (Múltiplo - 1) × 100
   
   Exemplo:
   Preço entrada: $0.000062
   Preço atual:   $0.000124
   Múltiplo: 2.0x (100% de alta)
   ```

3. **Verifica se atingiu Take Profit** (baseado no score):

   **Score 15-17:**
   - TP1: 2.0x → Vende 50%
   - TP2: 4.0x → Vende 20%
   - TP3: 8.0x → Vende 15%

   **Score 18-19:**
   - TP1: 1.5x → Vende 50%
   - TP2: 3.0x → Vende 50%

   **Score 20-21:**
   - TP1: 1.5x → Vende 50%
   - TP2: 2.5x → Vende 50%

4. **Executa venda parcial** quando atinge TP:
   - Vende percentual configurado
   - Converte tokens → SOL via Jupiter
   - Atualiza quantidade restante
   - Continua monitorando o resto

5. **Remove posição** quando vende 100% dos tokens

---

## 💰 Sistema de Valores por Score

| Score | Valor (SOL) | Valor (USD ~) | Tempo Máx | Take Profits |
|-------|-------------|---------------|-----------|--------------|
| 15-17 | 0.05 SOL | $5 | 3 min | 2x→50%, 4x→20%, 8x→15% |
| 18-19 | 0.03 SOL | $3 | 5 min | 1.5x→50%, 3x→50% |
| 20-21 | 0.02 SOL | $2 | 1 min | 1.5x→50%, 2.5x→50% |
| <15   | 0.01 SOL | $1 | - | Se habilitado |

---

## 📊 Exemplo Prático Completo

### Cenário: Token com Score 16

**1. Detecção:**
```
Token: BONK
Score: 16
Preço: $0.00001
Tempo: Detectado há 2 minutos
```

**2. Validações:**
- ✅ Bot ativo
- ✅ Score 16 está entre 15-21
- ✅ Tem valor configurado (0.05 SOL)
- ✅ Dentro da janela (2 min < 3 min máximo)
- ✅ Token novo (não comprado antes)

**3. Compra:**
```
Investindo: 0.05 SOL (~$5 USD)
Compra: 500.000 tokens BONK
Preço entrada: $0.00001
TX: 3k5j2h1g9f8e7d6c5b4a3...
```

**4. Monitoramento:**

| Tempo | Preço Atual | Múltiplo | % Alta | Ação |
|-------|-------------|----------|--------|------|
| T+0s  | $0.00001 | 1.0x | 0% | Comprado |
| T+10s | $0.000012 | 1.2x | 20% | Monitorando |
| T+30s | $0.000015 | 1.5x | 50% | Monitorando |
| T+1min | $0.00002 | **2.0x** | **100%** | **TP1: Vende 50%** |
| T+2min | $0.00003 | 3.0x | 200% | Monitorando |
| T+3min | $0.00004 | **4.0x** | **300%** | **TP2: Vende 20%** |
| T+5min | $0.00008 | **8.0x** | **700%** | **TP3: Vende 15%** |
| T+6min | $0.00009 | 9.0x | 800% | Monitorando 15% restante |

**5. Resultado Final:**
- Entrada: 500.000 tokens (0.05 SOL)
- TP1 (50%): 250.000 tokens → 0.025 SOL
- TP2 (20%): 100.000 tokens → 0.01 SOL  
- TP3 (15%): 75.000 tokens → 0.015 SOL
- Restante (15%): 75.000 tokens ainda em carteira
- **Total vendido: 0.05 SOL + lucro** (se preço continuar subindo)

---

## 🔧 Componentes do Sistema

### **bot.py**
- Conecta ao Telegram
- Monitora mensagens do canal
- Processa detecção de tokens
- Executa compras
- Orquestra todo o fluxo

### **message_parser.py**
- Faz parse das mensagens do Telegram
- Extrai informações do token (símbolo, preço, score, CA)

### **jupiter_client.py**
- Cliente da Jupiter API
- Executa swaps (compra/venda)
- Usa SOL como moeda base

### **take_profit.py**
- Monitora preços em tempo real
- Calcula múltiplos e % de alta
- Executa vendas parciais automaticamente
- Gerencia múltiplas posições simultaneamente

### **price_monitor.py**
- Busca preços em múltiplas fontes
- Fallback automático entre APIs
- Suporta: BirdEye, Jupiter, DexScreener

### **config.py**
- Todas as configurações do bot
- Valores por score
- Tempos máximos
- Take profit settings

### **web_interface.py**
- Interface web (localhost:5000)
- Visualiza trades ativos e vendidos
- Controla bot (ativar/desativar)
- Mostra estatísticas e lucros

---

## 🎛️ Controles Disponíveis

### Via Interface Web (http://localhost:5000)
- ✅ Ver trades ativos
- ✅ Ver histórico de vendas
- ✅ Ativar/desativar bot
- ✅ Ver último token detectado
- ✅ Ver saldo da carteira

### Via Configuração (.env)
- Valores por score
- Tempos máximos de compra
- Take profit levels
- APIs keys (opcional)
- Telegram channel

---

## ⚠️ Importante

1. **Bot usa SOL** para comprar tokens (não USDC)
2. **Regra de timing**: Bot só compra se token foi detectado dentro da janela de tempo
3. **Take profit escalonado**: Vendas parciais para maximizar lucros
4. **Monitoramento contínuo**: Loop de 10 segundos verifica preços
5. **Pode ser pausado**: Interface web permite ativar/desativar sem perder detecções

---

## 🚀 Como Iniciar

```bash
# Opção 1: Bot + Interface Web juntos
python run_all.py

# Opção 2: Apenas o bot
python bot.py

# Opção 3: Apenas interface web
python run_web.py
```

Interface web: http://localhost:5000











