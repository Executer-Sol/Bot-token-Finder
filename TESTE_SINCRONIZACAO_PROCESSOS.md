# Teste: Sincronização entre Processos Separados

## 🔄 Como Funciona a Sincronização

### Dois Processos Separados:

1. **Processo 1: Bot** (`python bot.py`)
   - Roda continuamente
   - Detecta mensagens do Telegram
   - Faz trades

2. **Processo 2: Site** (`python run_web.py`)
   - Roda servidor Flask na porta 5000
   - Interface web para configurar valores
   - Salva mudanças no arquivo `.env`

### ✅ Como a Sincronização Funciona:

**1. Site atualiza `.env`:**
```
Usuário muda valor no site → Site salva no arquivo .env
```

**2. Bot recarrega do arquivo:**
```
Bot processa nova mensagem → chama config.reload_config()
→ load_dotenv(override=True) → Lê arquivo .env novamente
→ Atualiza variáveis em memória
```

### 📁 O Arquivo `.env` é o "Meio de Comunicação"

```
┌─────────────┐         ┌──────────┐         ┌─────────────┐
│   Site      │  Salva  │   .env   │  Lê     │    Bot      │
│ (Processo 2)│────────>│ (Arquivo)│<────────│ (Processo 1)│
└─────────────┘         └──────────┘         └─────────────┘
```

### ⚙️ Como `reload_config()` Funciona:

```python
def reload_config():
    # Força recarregar do arquivo
    load_dotenv(override=True)  # override=True = sobrescreve valores em memória
    
    # Atualiza variáveis globais
    AMOUNT_SOL_15_17 = float(os.getenv('AMOUNT_SOL_15_17', '0.05'))
    # ... outras variáveis
```

### 🔍 Teste Prático:

**Cenário:** Você muda valor no site de 0.01 para 0.02 SOL

**Timeline:**
1. **T=0s:** Site salva `AMOUNT_SOL_15_17=0.02` no `.env`
2. **T=5s:** Bot recebe nova mensagem do Telegram
3. **T=5s:** Bot chama `config.reload_config()`
4. **T=5s:** Bot lê `.env` e vê `0.02`
5. **T=5s:** Bot usa `0.02` para o próximo trade

### ✅ Resultado do Teste:

- ✅ `load_dotenv(override=True)` **LÊ O ARQUIVO** a cada chamada
- ✅ Não usa cache - sempre lê do disco
- ✅ Funciona entre processos separados
- ✅ Bot pega mudanças do site automaticamente

### ⚠️ Importante:

- **Não precisa reiniciar o bot**
- **Não precisa reiniciar o site**
- **Sincronização é automática via arquivo `.env`**
- **Bot recarrega a cada mensagem** (próxima vez que processar token)

---

## 📝 Resumo:

| Processo | Ação | Resultado |
|----------|------|-----------|
| Site | Salva no `.env` | Arquivo atualizado |
| Bot (próxima mensagem) | `reload_config()` → `load_dotenv(override=True)` | Lê arquivo → Pega valor novo |

**✅ Funciona perfeitamente entre processos separados!**





