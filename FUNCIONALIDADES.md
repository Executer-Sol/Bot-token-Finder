# 📊 Guia Completo de Funcionalidades

Este documento explica cada aba e função da interface web do bot.

## 🏠 Página Inicial

Ao acessar http://localhost:5000, você verá:

### Controles Principais (Topo)
- **Status do Bot:** Mostra se bot está ATIVO ou DESATIVADO
- **Botão Ativar/Desativar:** Controla se bot compra tokens automaticamente
- **Saldo da Carteira:** Mostra SOL e USDC disponíveis
- **Estatísticas:** Tokens ativos, vendidos, lucro total, win rate

---

## 📑 Abas da Interface

### 1. 🟢 **Aba: Tokens Ativos**

**O que mostra:**
- Todos os tokens que você comprou e ainda está segurando
- Preço de entrada vs preço atual
- Percentual de lucro/perda
- Quantidade ainda segurando (pode ter vendido parcialmente)

**Colunas:**
- **Token:** Nome do token
- **Score:** Score do token quando foi detectado
- **Entrada:** Preço de compra
- **Atual:** Preço atual do token
- **%:** Percentual de alta/queda
- **Valor:** Valor atual em SOL
- **Segurando:** Percentual ainda na carteira
- **Comprado:** Data e horário da compra
- **Tempo:** Tempo decorrido desde a compra
- **Ações:** Botão para vender manualmente

**Para que serve:**
- Monitorar tokens que você está segurando
- Ver performance em tempo real
- Decidir quando vender manualmente

---

### 2. 📅 **Aba: Resumo do Dia - Tokens Ativos**

**O que mostra:**
- Cards detalhados de cada token ativo
- Informações visuais mais completas
- Barra de progresso mostrando quanto ainda está segurando

**Informações exibidas:**
- Símbolo e Score do token
- Múltiplo atual (ex: 2.5x)
- Preço de entrada e atual
- Valor investido e valor atual
- Percentual segurando (com barra visual)
- Data e horário de compra
- Tempo decorrido desde a compra
- Botão para marcar como vendido

**Para que serve:**
- Visualização mais detalhada dos tokens ativos
- Análise visual de performance
- Controle rápido de vendas

---

### 3. ✅ **Aba: Tokens Vendidos**

**O que mostra:**
- Histórico completo de todos os tokens que você vendeu
- Resultado de cada trade (lucro/perda)
- Motivo da venda

**Colunas:**
- **Token:** Nome do token
- **Score:** Score quando foi comprado
- **Entrada:** Preço de compra
- **Saída:** Preço de venda
- **Múltiplo:** Múltiplo final (ex: 2.5x)
- **%:** Percentual de lucro/perda
- **Lucro (SOL):** Lucro ou perda em SOL
- **Comprado:** Data e horário da compra
- **Vendido:** Data e horário da venda
- **Tempo até Venda:** Quanto tempo ficou segurando
- **Motivo:** Por que foi vendido (Take Profit, Stop Loss, Manual)

**Para que serve:**
- Analisar histórico de trades
- Ver quais estratégias funcionaram melhor
- Calcular ROI total
- Entender padrões de tempo (quanto tempo tokens levam para subir/cair)

---

### 4. 💰 **Aba: Valores de Compra por Score**

**O que mostra:**
- Configurações de quanto investir em cada score
- Tempo máximo para compra por score

**Configurações:**
- **Score 15-17:** Valor em SOL e tempo máximo (minutos)
- **Score 18-19:** Valor em SOL e tempo máximo (minutos)
- **Score 20-21:** Valor em SOL e tempo máximo (minutos)
- **Score <15:** Valor em SOL (se habilitado)

**Para que serve:**
- Ajustar quanto investir em cada tipo de token
- Controlar risco por score
- Ajustar janela de tempo para compra
- Mudanças são aplicadas automaticamente (sem reiniciar bot)

**Como usar:**
1. Ajuste os valores desejados
2. Clique em "Salvar Valores de Compra"
3. Bot usa novos valores automaticamente

---

### 5. ⚙️ **Aba: Configurações**

**O que mostra:**
- Configurações de Take Profit e Stop Loss
- Limite de perda diário

**Take Profit por Score:**
- **Score 15-17:** 3 níveis de TP (ex: 2x→50%, 4x→20%, 8x→15%)
- **Score 18-19:** 2 níveis de TP (ex: 1.5x→50%, 3x→50%)
- **Score 20-21:** 2 níveis de TP (ex: 1.5x→50%, 2.5x→50%)

**Stop Loss:**
- Tempo máximo antes de vender (minutos)
- Múltiplo mínimo esperado

**Para que serve:**
- Ajustar estratégia de vendas
- Controlar quando vender parcialmente
- Proteger contra perdas grandes

---

### 6. 📊 **Aba: Análise de Performance**

**O que mostra:**
- Estatísticas detalhadas de performance
- Análise por score
- Top 5 melhores e piores tokens

**Seções:**

**Performance por Score:**
- Total de tokens vendidos por range de score
- Win Rate (percentual de trades lucrativos)
- ROI Médio (retorno médio)
- Lucro Total

**Top 5 Melhores Tokens:**
- Tokens que mais deram lucro
- Múltiplo atingido
- Tempo até pico

**Top 5 Piores Tokens:**
- Tokens que mais deram prejuízo
- Múltiplo final
- Tempo até pico

**Para que serve:**
- Analisar quais scores são mais lucrativos
- Identificar padrões de sucesso
- Ajustar estratégia baseado em dados reais

---

### 7. 🧠 **Aba: Inteligência - Análise de Tokens Detectados**

**O que mostra:**
- Análise de todos os tokens detectados (mesmo os não comprados)
- Performance de tokens que você não comprou
- Insights sobre oportunidades perdidas

**Para que serve:**
- Ver se perdeu oportunidades
- Analisar se filtros estão muito restritivos
- Ajustar estratégia baseado em dados

---

### 8. 👁️ **Aba: Tokens Detectados**

**O que mostra:**
- Lista completa de todos os tokens que o bot detectou
- Mesmo os que não foram comprados
- Preços atualizados em tempo real

**Filtros disponíveis:**
- Buscar por símbolo ou Contract Address
- Filtrar por Score (15-17, 18-19, 20-21, <15)
- Filtrar por Status (Comprados, Não Comprados)
- Filtrar por Performance (Lucro, Prejuízo, Alto Múltiplo)

**Informações:**
- Símbolo e Score
- Preço inicial vs preço atual
- Múltiplo atual
- Status (comprado ou não)
- Botão para atualizar preço manualmente

**Para que serve:**
- Ver todos os tokens que passaram pelo canal
- Analisar oportunidades perdidas
- Acompanhar performance de tokens não comprados
- Exportar dados para análise (CSV)

---

### 9. 🚫 **Aba: Blacklist**

**O que mostra:**
- Lista de tokens bloqueados
- Bot não compra tokens na blacklist

**Para que serve:**
- Bloquear tokens que você não quer comprar
- Evitar tokens problemáticos
- Controlar quais tokens o bot pode comprar

**Como usar:**
1. Cole o Contract Address do token
2. Clique em "Adicionar à Blacklist"
3. Bot ignora este token automaticamente

---

## 🛠️ Funcionalidades Especiais

### Compra Manual
- **Onde:** Aba "Tokens Ativos" (seção no topo)
- **Como usar:**
  1. Cole o Contract Address do token
  2. Informe quantidade em SOL
  3. Clique em "Comprar Token"
  4. Bot compra na blockchain imediatamente

**Para que serve:**
- Comprar tokens que o bot não comprou automaticamente
- Comprar tokens de outras fontes
- Testar compras antes de ativar bot automático

### Venda Manual
- **Onde:** Aba "Tokens Ativos" (seção no topo)
- **Como usar:**
  1. Cole o Contract Address do token
  2. Informe percentual a vender (1-100%)
  3. Informe preço de venda
  4. Confirme a venda
  5. Bot vende na blockchain imediatamente

**Para que serve:**
- Vender tokens manualmente quando quiser
- Vender parcialmente (ex: 50%)
- Vender tokens que o bot ainda está segurando

### Atualização de Preços
- Botões para atualizar preços manualmente
- Atualiza preços de tokens ativos, vendidos e detectados
- Útil quando preços não estão atualizando automaticamente

---

## 📈 Métricas e Estatísticas

### Estatísticas Gerais (Topo da página)
- **Tokens Ativos:** Quantos tokens você está segurando
- **Tokens Vendidos:** Total de tokens vendidos
- **Lucro Total:** Soma de todos os lucros/perdas
- **Win Rate:** Percentual de trades lucrativos
- **ROI Médio:** Retorno médio sobre investimento

### Análise de Performance
- Performance por score (15-17, 18-19, 20-21)
- Tempo médio até pico
- Tempo médio até venda
- Múltiplo médio atingido

---

## 💡 Dicas de Uso

1. **Comece com valores pequenos** para testar
2. **Monitore a aba "Análise de Performance"** para ajustar estratégia
3. **Use a blacklist** para evitar tokens problemáticos
4. **Ajuste valores de compra** baseado em performance
5. **Revise tokens vendidos** para entender padrões
6. **Use compra/venda manual** para controle fino

---

## 🔄 Atualizações em Tempo Real

- Preços são atualizados automaticamente
- Estatísticas são recalculadas em tempo real
- Interface atualiza a cada 30 segundos
- Use Ctrl+R para atualizar manualmente

---

## ❓ Dúvidas?

Consulte:
- [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md) - Como instalar
- [GUIA_TELEGRAM.md](GUIA_TELEGRAM.md) - Como configurar Telegram
- [README.md](README.md) - Visão geral do projeto
