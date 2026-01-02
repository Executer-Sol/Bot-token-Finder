# 📖 Guia Completo de Instalação

Este guia vai te ajudar passo a passo a configurar o bot do zero.

## 📋 Pré-requisitos

Antes de começar, você precisa ter:

1. ✅ **Python 3.8 ou superior** instalado
2. ✅ **Conta no Telegram** (para obter API ID e Hash)
3. ✅ **Carteira Solana** com SOL para trading
4. ✅ **Conexão com internet** estável

---

## 🚀 Passo 1: Instalar Python

### Windows

1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente (3.8+)
3. Execute o instalador
4. **IMPORTANTE**: Marque a opção "Add Python to PATH"
5. Clique em "Install Now"
6. Aguarde a instalação
7. Verifique: Abra o CMD e digite `python --version`

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

### Mac

```bash
# Se tiver Homebrew:
brew install python3

# Ou baixe em: https://www.python.org/downloads/
python3 --version
```

---

## 📥 Passo 2: Baixar o Código

### Opção A: Usando Git (Recomendado)

```bash
git clone https://github.com/SEU_USUARIO/telegram_trading_bot.git
cd telegram_trading_bot
```

### Opção B: Baixar ZIP

1. Acesse o repositório no GitHub
2. Clique em "Code" → "Download ZIP"
3. Extraia o arquivo
4. Abra o terminal na pasta extraída

---

## 🔧 Passo 3: Criar Ambiente Virtual

Isola as dependências do projeto:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no início da linha do terminal.

---

## 📦 Passo 4: Instalar Dependências

```bash
pip install -r requirements.txt
```

Se der erro, instale manualmente:

```bash
pip install telethon python-dotenv solana aiohttp solders base58 flask flask-cors
```

---

## 🔑 Passo 5: Obter Credenciais do Telegram

### 5.1. Acessar my.telegram.org

1. Acesse: https://my.telegram.org/apps
2. Faça login com seu número de telefone
3. Você receberá um código no Telegram
4. Digite o código no site

### 5.2. Criar Aplicação

1. Clique em "API development tools"
2. Preencha o formulário:
   - **App title**: Trading Bot (ou qualquer nome)
   - **Short name**: bot (ou qualquer nome curto)
   - **Platform**: Desktop
   - **Description**: (opcional)
3. Clique em "Create application"

### 5.3. Copiar Credenciais

Você verá:
- **api_id**: Um número (ex: 12345678)
- **api_hash**: Uma string longa (ex: abcdef1234567890...)

**Anote esses valores!** Você vai precisar deles.

---

## 💼 Passo 6: Configurar Carteira Solana

### 6.1. Criar/Usar Carteira

**⚠️ IMPORTANTE**: Use uma carteira **SEPARADA** apenas para o bot!

**Opção A: Usar Phantom**
1. Instale Phantom: https://phantom.app/
2. Crie uma nova carteira
3. Exporte a chave privada:
   - Settings → Security & Privacy → Export Private Key
   - Digite sua senha
   - **CUIDADO**: Não compartilhe essa chave!

**Opção B: Usar Solflare**
1. Instale Solflare: https://solflare.com/
2. Crie uma nova carteira
3. Exporte a chave privada

### 6.2. Adicionar SOL

1. Transfira SOL para a carteira
2. Deixe um pouco extra para taxas (0.1-0.5 SOL)
3. **NÃO use sua carteira principal!**

---

## 📱 Passo 7: Descobrir ID do Canal/Grupo

O bot precisa saber qual canal monitorar.

### Método 1: Usar ID do Grupo (Recomendado)

1. Adicione o bot [@userinfobot](https://t.me/userinfobot) ao grupo
2. O bot mostrará o ID (ex: `-1001234567890`)
3. **Anote esse ID!**

### Método 2: Usar Script do Bot

```bash
python descobrir_grupo.py
```

O script mostrará todos os grupos disponíveis.

### Método 3: Usar Nome do Grupo

Use o nome exato do grupo/canal.

---

## ⚙️ Passo 8: Configurar .env

1. Copie o arquivo de exemplo:

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

2. Abra o arquivo `.env` em um editor de texto

3. Preencha com suas informações:

```env
# Telegram
TELEGRAM_API_ID=12345678                    # Seu API ID
TELEGRAM_API_HASH=abcdef1234567890...       # Seu API Hash
TELEGRAM_PHONE=+5511999999999                # Seu número com código do país
TELEGRAM_CHANNEL=-1001234567890             # ID do canal/grupo

# Solana
SOLANA_PRIVATE_KEY=sua_chave_privada_aqui    # Sua chave privada
RPC_URL=https://solana-mainnet.g.alchemy.com/v2/SEU_API_KEY  # RPC URL

# Valores de compra (ajuste conforme necessário)
AMOUNT_SOL_15_17=0.01
AMOUNT_SOL_18_19=0.01
AMOUNT_SOL_20_21=0.01
```

4. **Salve o arquivo**

---

## 🧪 Passo 9: Testar Conexão

### Testar Telegram

```bash
python testar_telegram.py
```

Na primeira vez, você receberá um código no Telegram. Digite o código.

### Testar Carteira

```bash
python wallet_balance.py
```

Deve mostrar seu saldo de SOL.

---

## 🚀 Passo 10: Iniciar o Bot

### Terminal 1: Bot Principal

```bash
python bot.py
```

Na primeira vez, você receberá um código no Telegram. Digite o código.

### Terminal 2: Interface Web (Opcional)

```bash
python run_web.py
```

Acesse: http://localhost:5000

---

## ✅ Verificação Final

O bot está funcionando se você ver:

1. ✅ "Bot conectado ao Telegram!"
2. ✅ "Grupo encontrado..."
3. ✅ "Bot ativo! Aguardando novos tokens..."
4. ✅ Interface web abre em http://localhost:5000

---

## 🆘 Problemas Comuns

### Erro: "Module not found"

```bash
pip install -r requirements.txt
```

### Erro: "Invalid API ID/Hash"

- Verifique se copiou corretamente do my.telegram.org
- Não tenha espaços extras

### Erro: "Group not found"

- Verifique o `TELEGRAM_CHANNEL` no `.env`
- Use o ID do grupo (recomendado)
- Execute `python descobrir_grupo.py`

### Erro: "Invalid private key"

- Verifique se copiou a chave privada completa
- Não tenha espaços ou quebras de linha

### Bot não compra tokens

- Verifique se bot está ativado (interface web)
- Verifique saldo de SOL
- Verifique `MIN_SCORE` e `MAX_SCORE`
- Verifique se tokens estão dentro da janela de tempo

---

## 📚 Próximos Passos

1. ✅ Configure valores de compra no `.env`
2. ✅ Ajuste take profits conforme sua estratégia
3. ✅ Teste com valores pequenos primeiro
4. ✅ Monitore performance na interface web
5. ✅ Ajuste configurações conforme necessário

**Pronto! Seu bot está configurado! 🎉**

