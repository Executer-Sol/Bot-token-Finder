# 📊 Análise de Performance - Para que serve?

## 🎯 Objetivo

A função `performance_analysis` analisa os **tokens vendidos** para identificar:
- Quais tokens foram os **melhores** (mais lucro)
- Quais tokens foram os **piores** (mais perda)
- **Métricas de tempo** (quanto tempo levou para subir/vender)
- **Padrões** que podem ajudar a melhorar a estratégia

---

## 📈 O que ela calcula:

### 1. **Top 5 Melhores Tokens** (`best_tokens`)
Lista os 5 tokens que deram **mais lucro**:
- Símbolo do token
- Score
- Lucro/Perda em SOL
- Tempo até atingir o pico
- Tempo até vender
- Múltiplo no pico
- Múltiplo final

**Para que serve:**
- Ver quais tokens foram os mais lucrativos
- Entender quais scores/comportamentos geram mais lucro
- Aprender com os sucessos

---

### 2. **Top 5 Piores Tokens** (`worst_tokens`)
Lista os 5 tokens que deram **mais perda**:
- Mesmas informações dos melhores
- Mostra os piores resultados

**Para que serve:**
- Identificar padrões que levam a perdas
- Evitar tokens similares no futuro
- Ajustar estratégia para evitar perdas

---

### 3. **Métricas de Tempo**

#### `avg_time_to_peak` (Tempo médio até o pico)
- Calcula a média de quanto tempo (minutos) os tokens levam para atingir o **maior valor**
- Exemplo: Se média é 3 minutos, significa que tokens bons geralmente sobem rápido

**Para que serve:**
- Validar se o stop loss de 5 minutos está adequado
- Se tokens bons sobem em média em 2 minutos, você está vendendo muito cedo ou muito tarde?
- Ajustar timing de compra/venda

#### `avg_time_to_sell` (Tempo médio até vender)
- Calcula a média de quanto tempo (minutos) os tokens ficaram na carteira até vender
- Exemplo: Se média é 5 minutos, é quanto tempo você está segurando tokens em média

**Para que serve:**
- Entender tempo médio de retenção
- Verificar se está vendendo muito rápido ou muito lento
- Comparar com o `STOP_LOSS_TIME_MINUTES` (5 minutos padrão)

#### `avg_peak_multiple` (Múltiplo médio no pico)
- Calcula a média do **maior múltiplo** que os tokens atingiram
- Exemplo: Se média é 2.5x, significa que em média tokens atingem 2.5x antes de vender

**Para que serve:**
- Ver se você está vendendo muito cedo (se pico médio é 5x mas você vende em 2x)
- Ajustar take profits (se tivesse)
- Entender potencial dos tokens

---

## 📊 Onde aparece no Dashboard:

A análise de performance aparece na aba **"Resumo do Dia"** do dashboard, mostrando:
- 📈 Top 5 melhores tokens (cards verdes)
- 📉 Top 5 piores tokens (cards vermelhos)
- ⏱️ Métricas de tempo (se houver dados suficientes)

---

## 💡 Exemplo Prático:

### Cenário: Você tem 20 tokens vendidos

**Análise mostra:**
```
Top 5 Melhores:
1. TOKEN_A - Score 17 - +0.15 SOL - Pico: 3.2x em 2 min
2. TOKEN_B - Score 19 - +0.12 SOL - Pico: 2.8x em 3 min
...

Tempo médio até pico: 2.5 minutos
Tempo médio até vender: 5.2 minutos
Múltiplo médio no pico: 2.1x
```

**O que você aprende:**
- ✅ Tokens bons sobem rápido (2.5 min em média)
- ✅ Você está vendendo em média após 5.2 min (compatível com stop loss de 5 min)
- ✅ Tokens atingem 2.1x em média (você poderia ter take profit em 2x para garantir lucro)
- ✅ Score 17-19 parece estar performando bem

---

## 🎯 Resumo:

| Métrica | O que mostra | Para que serve |
|---------|--------------|----------------|
| `best_tokens` | Top 5 mais lucrativos | Aprender com sucessos |
| `worst_tokens` | Top 5 mais perdas | Evitar padrões ruins |
| `avg_time_to_peak` | Tempo médio até máximo | Validar timing de compra |
| `avg_time_to_sell` | Tempo médio até vender | Validar stop loss time |
| `avg_peak_multiple` | Múltiplo médio no pico | Ajustar take profits |

---

## ⚠️ Importante:

- ✅ Só funciona com **tokens vendidos** (não mostra tokens ativos)
- ✅ Precisa ter dados de `time_to_peak` e `time_to_sell` (salvos pelo bot quando vende)
- ✅ Quanto mais trades, mais confiável a análise
- ✅ Ajuda a **melhorar a estratégia** baseado em dados reais

**Em resumo: É uma ferramenta de análise para entender o desempenho do bot e ajustar a estratégia!**





