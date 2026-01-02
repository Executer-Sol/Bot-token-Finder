# 📖 Guia Completo para Iniciantes - Bot de Trading

## 🎯 O Que Este Bot Faz?

Este bot **automaticamente**:
1. 📱 Monitora canais do Telegram procurando novos tokens
2. 🔍 Analisa cada token e dá uma "nota" (score)
3. 💰 Compra tokens automaticamente se a nota for boa
4. 📈 Monitora o preço e vende quando atinge seus objetivos
5. 📊 Mostra tudo em uma interface web bonita

**Você não precisa fazer nada!** O bot trabalha sozinho. Mas você pode controlar tudo pela interface web.

---

## 🖥️ Interface Web - Explicação de Cada Aba

Quando você acessa http://localhost:5000, você vê uma interface com várias abas. Vamos explicar cada uma:

---

### 🟢 **ABA 1: Tokens Ativos**

**O que é?**
- Lista de todos os tokens que você **comprou e ainda está segurando**
- Como uma "carteira" mostrando seus investimentos ativos

**O que você vê:**
- Nome do token (ex: BONK, PEPE)
- Score (nota que o token tinha quando foi comprado)
- Preço de entrada (quanto você pagou)
- Preço atual (quanto vale agora)
- Percentual de lucro/perda (+50% = lucro, -20% = perda)
- Quanto ainda está segurando (pode ter vendido 50% e ainda ter 50%)

**Para que serve?**
- Ver se seus tokens estão dando lucro ou prejuízo
- Decidir se quer vender manualmente
- Acompanhar performance em tempo real

**Exemplo:**
```
Token: BONK
Score: 16
Entrada: $0.00001
Atual: $0.00002
%: +100% (dobrou!)
Segurando: 50% (você já vendeu 50% antes)
```

---

### 📅 **ABA 2: Resumo do Dia - Tokens Ativos**

**O que é?**
- Mesma coisa da aba "Tokens Ativos", mas com **visualização mais bonita**
- Cards grandes e coloridos ao invés de tabela

**O que você vê:**
- Cards grandes para cada token
- Barra de progresso mostrando quanto ainda está segurando
- Informações mais detalhadas e visuais
- Histórico de vendas parciais (se vendeu 50% antes, mostra quando e por quanto)

**Para que serve?**
- Visualização mais fácil e bonita
- Ver tudo de uma vez sem precisar rolar tabela
- Melhor para análise rápida

---

### ✅ **ABA 3: Tokens Vendidos**

**O que é?**
- Histórico de **todos os tokens que você já vendeu completamente**
- Como um "extrato" de todas as suas vendas

**O que você vê:**
- Nome do token
- Preço que comprou vs preço que vendeu
- Lucro ou perda em SOL
- Quanto tempo ficou segurando (5 minutos? 2 horas?)
- Por que foi vendido (Take Profit automático? Você vendeu manual? Stop Loss?)

**Para que serve?**
- Ver histórico de todas as operações
- Calcular lucro total
- Entender quais estratégias funcionaram melhor
- Ver padrões (tokens que sobem rápido, tokens que demoram, etc)

**Exemplo:**
```
Token: PEPE
Comprou: $0.00005
Vendeu: $0.00010
Lucro: +0.05 SOL
Tempo: 15 minutos
Motivo: Take Profit (bot vendeu automaticamente quando dobrou)
```

---

### 💰 **ABA 4: Valores de Compra por Score**

**O que é?**
- Configurações de **quanto dinheiro investir em cada tipo de token**
- Baseado na "nota" (score) do token

**O que você configura:**
- **Score 15-17:** Quanto investir (ex: 0.05 SOL) e tempo máximo (ex: 3 minutos)
- **Score 18-19:** Quanto investir (ex: 0.03 SOL) e tempo máximo (ex: 5 minutos)
- **Score 20-21:** Quanto investir (ex: 0.02 SOL) e tempo máximo (ex: 1 minuto)
- **Score <15:** Se quer comprar tokens com nota baixa (geralmente não recomendado)

**Para que serve?**
- Controlar quanto dinheiro arriscar em cada tipo de token
- Tokens com nota melhor = pode investir mais
- Tokens com nota pior = investir menos ou não investir
- Mudanças são aplicadas **automaticamente** (não precisa reiniciar bot)

**Exemplo:**
```
Score 15-17: Investir 0.05 SOL (tokens mais seguros, pode investir mais)
Score 20-21: Investir 0.02 SOL (tokens muito novos, investir menos)
```

---

### ⚙️ **ABA 5: Configurações**

**O que é?**
- Configurações de **quando e como vender** os tokens
- Take Profit (vender quando lucrar) e Stop Loss (vender para evitar perda)

**O que você configura:**

**Take Profit (Vender quando lucrar):**
- Para cada score, você define:
  - Múltiplo (ex: 2x = quando dobrar o preço)
  - Percentual a vender (ex: 50% = vende metade, mantém metade)
  
**Exemplo:**
```
Score 15-17:
- Quando atingir 2x → Vender 50% (garante lucro, mantém 50% para subir mais)
- Quando atingir 4x → Vender mais 20% (lucro maior)
- Quando atingir 8x → Vender mais 15% (lucro máximo)
```

**Stop Loss (Vender para evitar perda):**
- Tempo máximo (ex: 5 minutos) - se não subir em 5 minutos, vende tudo
- Múltiplo mínimo esperado (ex: 1.0x) - se cair muito, vende

**Para que serve?**
- Automatizar vendas inteligentes
- Garantir lucro quando token sobe
- Evitar perdas grandes quando token cai
- Vender parcialmente (não vender tudo de uma vez)

---

### 📊 **ABA 6: Análise de Performance**

**O que é?**
- Estatísticas detalhadas de **como o bot está performando**
- Análise de quais estratégias funcionam melhor

**O que você vê:**

**Performance por Score:**
- Quantos tokens de cada score foram vendidos
- Win Rate (percentual de trades que deram lucro)
- ROI Médio (retorno médio)
- Lucro Total por score

**Top 5 Melhores Tokens:**
- Tokens que mais deram lucro
- Quanto tempo levou para subir
- Múltiplo máximo atingido

**Top 5 Piores Tokens:**
- Tokens que mais deram prejuízo
- Para aprender o que evitar

**Para que serve?**
- Entender quais scores são mais lucrativos
- Ajustar estratégia baseado em dados reais
- Ver se está ganhando ou perdendo dinheiro
- Identificar padrões de sucesso

**Exemplo:**
```
Score 15-17:
- Total vendidos: 10 tokens
- Win Rate: 70% (7 deram lucro, 3 deram prejuízo)
- ROI Médio: +25%
- Lucro Total: +0.5 SOL
```

---

### 🧠 **ABA 7: Inteligência - Análise de Tokens Detectados**

**O que é?**
- Análise de **todos os tokens que o bot detectou**, mesmo os que não comprou
- Para ver se você perdeu oportunidades

**O que você vê:**
- Tokens que o bot viu mas não comprou
- Como esses tokens performaram depois
- Se você deveria ter comprado ou não

**Para que serve?**
- Ver se filtros estão muito restritivos (perdendo boas oportunidades)
- Ajustar estratégia baseado em dados
- Entender se está sendo muito conservador ou muito arriscado

---

### 👁️ **ABA 8: Tokens Detectados**

**O que é?**
- Lista completa de **TODOS os tokens que o bot viu** no Telegram
- Mesmo os que não foram comprados

**O que você vê:**
- Todos os tokens que passaram pelo canal
- Preço inicial vs preço atual
- Se foi comprado ou não
- Performance atual

**Filtros disponíveis:**
- Buscar por nome ou endereço
- Filtrar por Score
- Filtrar por Status (Comprados, Não Comprados)
- Filtrar por Performance (Lucro, Prejuízo)

**Para que serve?**
- Ver todos os tokens que passaram
- Analisar oportunidades perdidas
- Acompanhar tokens que você não comprou
- Exportar dados para análise

---

### 🚫 **ABA 9: Blacklist**

**O que é?**
- Lista de tokens que você **NÃO quer que o bot compre**
- Tokens bloqueados

**O que você vê:**
- Lista de endereços de tokens bloqueados
- Botão para adicionar/remover

**Para que serve?**
- Bloquear tokens problemáticos
- Evitar tokens que você não confia
- Controlar quais tokens o bot pode comprar

**Como usar:**
1. Cole o Contract Address do token
2. Clique em "Adicionar à Blacklist"
3. Bot nunca mais compra este token

---

## 🛠️ Funcionalidades Especiais

### 💵 **Compra Manual**

**Onde:** Seção no topo da página (antes das abas)

**O que faz:**
- Permite comprar tokens **manualmente** sem esperar o bot
- Você escolhe qual token comprar e quanto investir

**Como usar:**
1. Cole o Contract Address do token
2. Digite quantidade em SOL (ex: 0.05)
3. Clique em "Comprar Token"
4. Bot compra na blockchain imediatamente

**Para que serve:**
- Comprar tokens que o bot não comprou automaticamente
- Comprar tokens de outras fontes
- Testar antes de ativar bot automático

---

### 💸 **Venda Manual**

**Onde:** Seção no topo da página (ao lado de Compra Manual)

**O que faz:**
- Permite vender tokens **manualmente** quando quiser
- Você escolhe quanto vender (100% ou parcial como 50%)

**Como usar:**
1. Cole o Contract Address do token
2. Digite percentual a vender (1-100%)
3. Digite o preço de venda
4. Confirme
5. Bot vende na blockchain imediatamente

**Para que serve:**
- Vender quando você quiser (não esperar Take Profit)
- Vender parcialmente (ex: vender 50%, manter 50%)
- Vender tokens que o bot ainda está segurando

---

## 📈 Estatísticas no Topo da Página

No topo da página, você sempre vê:

- **Tokens Ativos:** Quantos tokens você está segurando agora
- **Tokens Vendidos:** Total de tokens que você já vendeu
- **Lucro Total:** Soma de todos os lucros e perdas
- **Win Rate:** Percentual de trades que deram lucro
- **ROI Médio:** Retorno médio sobre investimento
- **Hoje:** Quantos tokens comprou hoje

---

## 💡 Dicas para Iniciantes

### ✅ **Comece Devagar:**
- Use valores pequenos no início (0.01 SOL)
- Teste por alguns dias antes de aumentar
- Acompanhe a aba "Análise de Performance"

### ✅ **Monitore Regularmente:**
- Verifique a aba "Tokens Ativos" algumas vezes por dia
- Veja se tokens estão performando bem
- Use a aba "Análise" para entender padrões

### ✅ **Use a Blacklist:**
- Se um token te deu prejuízo, adicione à blacklist
- Bloqueie tokens que você não confia
- Evite repetir erros

### ✅ **Ajuste Configurações:**
- Comece com Take Profit conservador (2x, 3x)
- Ajuste baseado em performance real
- Use a aba "Análise" para ver o que funciona

### ✅ **Não Entre em Pânico:**
- Tokens podem cair antes de subir
- Stop Loss protege contra perdas grandes
- Vendas parciais garantem lucro mesmo se token cair depois

---

## ❓ Perguntas Frequentes

### **O bot compra automaticamente?**
Sim! Quando você ativa o bot, ele monitora o Telegram e compra tokens automaticamente baseado nas configurações.

### **Preciso ficar olhando o tempo todo?**
Não! O bot trabalha sozinho. Mas é bom verificar algumas vezes por dia para ver como está indo.

### **Posso desativar o bot?**
Sim! Tem um botão no topo da página para ativar/desativar. Quando desativado, o bot não compra nada, mas continua mostrando tokens detectados.

### **E se eu quiser vender manualmente?**
Use a função "Venda Manual" no topo da página. Você escolhe qual token e quanto vender.

### **Como sei se está dando lucro?**
Veja a aba "Análise de Performance" e as estatísticas no topo. Win Rate mostra percentual de trades lucrativos.

### **Posso mudar configurações depois?**
Sim! Todas as configurações podem ser mudadas pela interface web e são aplicadas automaticamente.

---

## 🆘 Precisa de Ajuda?

Consulte os outros guias:
- **[GUIA_INSTALACAO.md](GUIA_INSTALACAO.md)** - Como instalar e configurar
- **[GUIA_TELEGRAM.md](GUIA_TELEGRAM.md)** - Como configurar o Telegram
- **[README.md](README.md)** - Visão geral do projeto

---

**🎉 Agora você entende tudo sobre o bot! Boa sorte com seus trades!**

