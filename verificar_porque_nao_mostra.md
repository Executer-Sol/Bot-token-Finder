# 🔍 Por Que o Bot Não Mostra Nada no Terminal?

## ❓ Problema

O bot está rodando, mas não mostra nada no terminal, nem mesmo quando há tokens.

---

## 🔍 Possíveis Motivos

### 1. **Bot está DESATIVADO**
- Se o bot está desativado, ele não mostra mensagens de tokens
- Verifique: http://localhost:5000
- Ative o bot se estiver desativado

### 2. **Mensagens não têm formato de token**
- Bot só mostra mensagens com formato de token
- Precisa ter: `#símbolo`, `Score:`, `CA:`, `$preço`
- Mensagens normais são ignoradas (não aparecem)

### 3. **Tokens estão fora da janela de tempo**
- Bot mostra mensagem quando detecta, mas pode não comprar
- Se estiver fora da janela, mostra: `⏭️ Token detectado há X minutos - FORA da janela`

### 4. **Bot não está recebendo mensagens**
- Problema de conexão Telegram
- Canal não configurado corretamente
- Bot não tem acesso ao canal

### 5. **Problema com logger**
- Logger pode não estar funcionando
- Verifique logs: `Get-Content logs\bot_*.log -Tail 50`

---

## ✅ Solução: Diagnóstico Completo

### **Passo 1: Rode o diagnóstico**

```bash
python diagnosticar_bot_silencioso.py
```

Este script vai:
- Verificar se bot está ATIVO
- Testar conexão Telegram
- Buscar canal configurado
- Monitorar mensagens e testar parse
- Simular o que o bot faria

**Envie uma mensagem com formato de token enquanto o script está rodando!**

### **Passo 2: Verifique estado do bot**

```bash
python verificar_ultimo_token.py
```

Mostra se o bot viu algum token recentemente.

### **Passo 3: Verifique logs**

```bash
Get-Content logs\bot_*.log -Tail 50
```

Procure por:
- Mensagens de erro
- Tokens detectados
- Tentativas de compra

---

## 📋 Checklist Rápido

- [ ] Bot está rodando? (`python run_all.py`)
- [ ] Bot está ATIVO? (http://localhost:5000)
- [ ] Canal está enviando mensagens?
- [ ] Mensagens têm formato de token?
- [ ] Verificou logs?

---

## 💡 O Que o Bot Mostra Quando Funciona

Quando o bot detecta um token válido, ele mostra:

```
🚀 Novo token detectado!
   Símbolo: DOGE2
   Score: 17
   Preço: $0.000076
   CA: 34qNuzuE1Y6KcAr...
   ⏱️  Tempo desde detecção: 2 minutos
   💰 Investindo: 0.05 SOL (baseado no score)
```

Se não mostra nada, pode ser:
- Bot desativado
- Mensagens sem formato de token
- Tokens fora da janela de tempo (mas deveria mostrar mensagem)
- Bot não está recebendo mensagens

---

## 🎯 Próximos Passos

1. **Rode o diagnóstico:**
   ```bash
   python diagnosticar_bot_silencioso.py
   ```

2. **Verifique último token:**
   ```bash
   python verificar_ultimo_token.py
   ```

3. **Verifique logs:**
   ```bash
   Get-Content logs\bot_*.log -Tail 50
   ```

O diagnóstico vai mostrar exatamente o que está acontecendo!











