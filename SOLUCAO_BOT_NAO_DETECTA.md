# 🔧 Solução: Bot Não Está Detectando Mensagens

## 🔍 Diagnóstico

Se o bot está rodando mas não detecta mensagens, pode ser:

### 1. **Bot não está recebendo mensagens do Telegram**
   - Event handler não está sendo acionado
   - Canal não está enviando mensagens
   - Bot não tem permissão para ler mensagens

### 2. **Canal não encontrado ou ID incorreto**
   - ID do canal incorreto no `.env`
   - Canal foi removido/alterado

### 3. **Mensagens não têm formato de token**
   - Bot só detecta mensagens com formato específico
   - Precisa ter: `#símbolo`, `Score:`, `CA:`, `$preço`

---

## ✅ Solução: Teste de Recebimento

### **Passo 1: Teste se o bot recebe mensagens**

```bash
python testar_recebimento_mensagens.py
```

Este script:
- Conecta ao Telegram
- Monitora o canal por 60 segundos
- Mostra TODAS as mensagens recebidas
- Indica se alguma tem formato de token

**Se não receber nenhuma mensagem:**
- ❌ Problema de conexão ou permissões
- Verifique se o canal está enviando mensagens
- Verifique se o bot tem acesso ao canal

**Se receber mensagens mas não detectar tokens:**
- ✅ Bot está recebendo (conexão OK)
- ❌ Mensagens não têm formato de token
- Verifique o formato das mensagens no canal

---

## 🔧 Verificações Adicionais

### **1. Verificar ID do Canal**

```bash
python descobrir_grupo.py
```

Lista todos os grupos/canais disponíveis com seus IDs.

### **2. Verificar Configuração**

Confirme no `.env`:
```env
TELEGRAM_CHANNEL=-1003268996940
```
(ou o nome do canal, se for público)

### **3. Verificar Logs**

```bash
Get-Content logs\bot_*.log -Tail 50
```

Procure por:
- "Grupo encontrado" → Canal foi encontrado
- "Monitorando canal" → Handler foi registrado
- Mensagens de erro

---

## 📋 Checklist

- [ ] Bot está rodando (`python run_all.py`)
- [ ] Bot está ATIVO (interface web)
- [ ] Canal existe e bot tem acesso
- [ ] Canal está enviando mensagens
- [ ] ID do canal está correto no `.env`
- [ ] Teste de recebimento mostra mensagens

---

## 💡 Próximos Passos

1. **Rode o teste:**
   ```bash
   python testar_recebimento_mensagens.py
   ```

2. **Se não receber mensagens:**
   - Verifique acesso ao canal
   - Verifique ID do canal
   - Teste com outro canal conhecido

3. **Se receber mensagens mas não detectar tokens:**
   - Formato da mensagem pode estar diferente
   - Verifique se mensagens têm: `#`, `Score:`, `CA:`, `$`
   - Cole uma mensagem exemplo e rode: `python diagnosticar_token.py`

---

## 🎯 Resumo

**Se o bot está parado e não detecta nada:**

1. ✅ Teste recebimento: `python testar_recebimento_mensagens.py`
2. ✅ Verifique logs: `Get-Content logs\bot_*.log -Tail 50`
3. ✅ Verifique canal: `python descobrir_grupo.py`

O teste vai mostrar se o problema é:
- **Não recebe mensagens** → Problema de conexão/permissão
- **Recebe mas não detecta** → Formato diferente ou parse falhando











