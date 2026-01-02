# 🔍 Por Que o Bot Não Comprou o Token?

## ❌ Motivos Comuns

### 1. **Bot não está rodando**
- Verifique se `python run_all.py` está rodando
- Verifique o terminal

### 2. **Bot está DESATIVADO**
- Abra: http://localhost:5000
- Verifique se o bot está **ATIVO** (toggle verde)
- Se estiver desativado, ative e tente novamente

### 3. **Parse falhou (mensagem não reconhecida)**
O bot precisa que a mensagem tenha:
- ✅ Símbolo com `#` (ex: `#oddbit`)
- ✅ Preço com `$` (ex: `$0.000062`)
- ✅ Score (ex: `Score: 15`)
- ✅ CA (ex: `CA: A6RTAd...`)

**Se faltar algum, o bot não detecta!**

### 4. **Score fora do range**
- Score mínimo: 15 (configurado)
- Score máximo: 21 (configurado)
- Se score < 15 ou > 21 → **NÃO COMPRA**

### 5. **Fora da janela de tempo** ⏱️
- **Score 15-17**: máximo 3 minutos
- **Score 18-19**: máximo 5 minutos
- **Score 20-21**: máximo 1 minuto

**Se detectado há mais tempo → NÃO COMPRA**

### 6. **Token na blacklist** 🚫
- Se o token está na blacklist → **NÃO COMPRA**
- Verifique na interface web: http://localhost:5000

### 7. **Limite de perda diário atingido** 💸
- Se perdeu mais que o limite hoje → **NÃO COMPRA**
- Verifique na interface web

### 8. **Score sem valor configurado**
- Score precisa ter valor em SOL configurado
- Verifique `config.py` ou `.env`

### 9. **Saldo insuficiente** 💰
- Precisa ter SOL suficiente na carteira
- Verifique saldo

### 10. **Token já foi comprado** 🔄
- Se já está negociando este token → **NÃO COMPRA NOVAMENTE**

### 11. **Erro de conexão (Jupiter API)** 🌐
- Problema de DNS com `quote-api.jup.ag`
- Bot pode detectar mas não consegue comprar

---

## 🔧 Como Diagnosticar

### **Opção 1: Script de Diagnóstico Completo**

```bash
python diagnosticar_token.py
```

Cole a mensagem do Telegram quando pedir e veja **TODOS os motivos** detalhados!

### **Opção 2: Teste Rápido de Parse**

```bash
python testar_parse_mensagem.py
```

Testa se a mensagem é reconhecida pelo parser.

### **Opção 3: Verificar Logs**

```bash
# Ver últimos logs
Get-Content logs\bot_*.log -Tail 50
```

Procure por:
- Mensagens de erro
- Tokens ignorados
- Motivos de rejeição

---

## 📋 Checklist Rápido

Antes de reportar problema, verifique:

- [ ] Bot está rodando? (`python run_all.py`)
- [ ] Bot está ATIVO na interface web? (http://localhost:5000)
- [ ] Mensagem tem formato correto? (#símbolo, $preço, Score, CA)
- [ ] Score dentro do range? (15-21)
- [ ] Dentro da janela de tempo? (veja tabela acima)
- [ ] Token não está na blacklist?
- [ ] Tem SOL suficiente na carteira?
- [ ] Token não foi comprado antes?

---

## 💡 Solução Rápida

**Se nada funcionar, rode o diagnóstico:**

```bash
python diagnosticar_token.py
```

Cole a mensagem exata do Telegram e veja o motivo detalhado!











