# 📱 Guia Completo: Como o Bot Coleta Dados do Telegram

Este guia explica **exatamente** como o bot se conecta ao Telegram e coleta informações sobre novos tokens.

---

## 🔍 Como Funciona

O bot usa a **API oficial do Telegram** (Telethon) para:

1. **Conectar** à sua conta do Telegram
2. **Monitorar** um canal/grupo específico
3. **Ler mensagens** em tempo real
4. **Extrair informações** dos tokens (símbolo, preço, score, CA)
5. **Decidir** se deve comprar ou não

---

## 📋 Passo a Passo: Configuração do Telegram

### Passo 1: Obter API ID e Hash

#### 1.1. Acessar my.telegram.org

1. Abra seu navegador
2. Acesse: **https://my.telegram.org/apps**
3. Faça login com seu número de telefone

#### 1.2. Receber Código

1. Você receberá um código no Telegram
2. Digite o código no site
3. Se não receber, clique em "Send code via SMS"

#### 1.3. Criar Aplicação

1. Clique em **"API development tools"**
2. Se for a primeira vez, preencha o formulário:

   - **App title**: `Trading Bot` (ou qualquer nome)
   - **Short name**: `bot` (ou qualquer nome curto)
   - **Platform**: Selecione `Desktop`
   - **Description**: (opcional) `Bot para trading automático`

3. Clique em **"Create application"**

#### 1.4. Copiar Credenciais

Você verá duas informações importantes:

- **api_id**: Um número (ex: `12345678`)
  - Copie este número
- **api_hash**: Uma string longa (ex: `abcdef1234567890abcdef1234567890`)
  - Copie esta string completa

**⚠️ IMPORTANTE**: 
- Não compartilhe essas credenciais
- Elas são únicas para sua conta
- Guarde em local seguro

#### 1.5. Adicionar ao .env

Abra o arquivo `.env` e adicione:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+5511999999999
```

**Formato do telefone**: `+` + código do país + número
- Brasil: `+5511999999999`
- EUA: `+11234567890`

---

### Passo 2: Descobrir o Canal/Grupo para Monitorar

O bot precisa saber **qual canal/grupo** monitorar. Você tem 3 opções:

#### Opção A: Usar ID do Grupo (⭐ Recomendado)

**Por quê?** O ID é único e não muda, mesmo se o nome do grupo mudar.

**Como fazer:**

1. Adicione o bot [@userinfobot](https://t.me/userinfobot) ao grupo
2. O bot mostrará informações do grupo, incluindo o ID
3. O ID será algo como: `-1001234567890`
4. Copie esse ID

**Adicionar ao .env:**
```env
TELEGRAM_CHANNEL=-1001234567890
```

#### Opção B: Usar Nome do Grupo

**Quando usar?** Se você souber o nome exato do grupo.

**Como fazer:**

1. Anote o nome **exato** do grupo/canal
2. Exemplo: `Meu Canal de Tokens`

**Adicionar ao .env:**
```env
TELEGRAM_CHANNEL=Meu Canal de Tokens
```

**⚠️ ATENÇÃO**: O nome deve ser **exatamente** igual, incluindo maiúsculas/minúsculas.

#### Opção C: Usar Username

**Quando usar?** Se o canal tiver username público (começa com @).

**Como fazer:**

1. Anote o username do canal
2. Exemplo: `@meucanal`

**Adicionar ao .env:**
```env
TELEGRAM_CHANNEL=@meucanal
```

---

### Passo 3: Testar Conexão

Antes de iniciar o bot completo, teste a conexão:

```bash
python testar_telegram.py
```

**O que acontece:**

1. O script tenta conectar ao Telegram
2. Se for a primeira vez, você receberá um **código** no Telegram
3. Digite o código no terminal
4. Se tudo estiver certo, verá: `✅ Conectado com sucesso!`

**Se der erro:**

- Verifique `TELEGRAM_API_ID` e `TELEGRAM_API_HASH`
- Verifique `TELEGRAM_PHONE` (formato: +5511999999999)
- Certifique-se de ter internet

---

### Passo 4: Descobrir Grupos Disponíveis

Se não souber o ID do grupo, use o script:

```bash
python descobrir_grupo.py
```

**O que acontece:**

1. O script lista todos os grupos/canais que você tem acesso
2. Mostra o **nome** e o **ID** de cada um
3. Escolha o ID do grupo que quer monitorar
4. Adicione ao `.env`

**Exemplo de saída:**
```
Grupos disponíveis:
- Meu Canal de Tokens (ID: -1001234567890)
- Outro Canal (ID: -1009876543210)
```

---

## 🔄 Como o Bot Monitora o Canal

### Fluxo de Funcionamento

```
1. Bot conecta ao Telegram
   ↓
2. Encontra o canal/grupo configurado
   ↓
3. Fica "escutando" novas mensagens
   ↓
4. Quando chega uma mensagem nova:
   ↓
5. Analisa se é uma mensagem de token
   ↓
6. Se for, extrai informações:
   - Símbolo (#TOKEN)
   - Preço ($0.0001)
   - Score (15-21)
   - Contract Address (CA)
   ↓
7. Verifica se deve comprar:
   - Score dentro do range?
   - Dentro da janela de tempo?
   - Saldo suficiente?
   - Não está na blacklist?
   ↓
8. Se tudo OK, compra automaticamente
```

### Exemplo de Mensagem que o Bot Detecta

```
#SHIRLEY ● $0.0₃82 82K FDV atualmente

Score: 16 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 4pts)

CA: FipAgs4hHCm5HBrD4rvAP8LGgrm1iWW4qgB1aTAYpump
```

**O bot extrai:**
- **Símbolo**: `SHIRLEY`
- **Preço**: `$0.000082`
- **Score**: `16`
- **CA**: `FipAgs4hHCm5HBrD4rvAP8LGgrm1iWW4qgB1aTAYpump`

---

## 🔐 Segurança e Privacidade

### O que o Bot Acessa?

- ✅ **Apenas o canal/grupo** que você configurou
- ✅ **Apenas mensagens** desse canal/grupo
- ❌ **NÃO acessa** suas conversas privadas
- ❌ **NÃO acessa** outros grupos
- ❌ **NÃO envia mensagens** (apenas lê)

### Suas Credenciais

- As credenciais (`api_id` e `api_hash`) são **únicas para sua conta**
- Elas **não dão acesso** à sua conta sem o código de verificação
- O código é enviado **sempre** para seu Telegram
- **Nunca compartilhe** suas credenciais

### Sessão do Telegram

- O bot cria um arquivo `session.session`
- Este arquivo mantém você logado
- **Não compartilhe** este arquivo
- Está no `.gitignore` (não será commitado)

---

## 🛠️ Troubleshooting

### Problema: "Invalid API ID/Hash"

**Solução:**
1. Verifique se copiou corretamente do my.telegram.org
2. Não tenha espaços extras antes/depois
3. Certifique-se de que não há quebras de linha

### Problema: "Group not found"

**Solução:**
1. Verifique o `TELEGRAM_CHANNEL` no `.env`
2. Use o ID do grupo (recomendado)
3. Execute `python descobrir_grupo.py` para ver grupos disponíveis
4. Certifique-se de que você tem acesso ao grupo

### Problema: "Phone number invalid"

**Solução:**
1. Use o formato: `+5511999999999`
2. Inclua o código do país (`+55` para Brasil)
3. Sem espaços ou hífens

### Problema: "Code not received"

**Solução:**
1. Verifique se o número está correto
2. Tente "Send code via SMS" no site
3. Verifique se não está bloqueado pelo Telegram

### Problema: Bot não detecta tokens

**Solução:**
1. Verifique se o canal está correto
2. Verifique se há mensagens de tokens no canal
3. Verifique os logs: `logs/bot_YYYYMMDD.log`
4. Certifique-se de que o bot está ativado (interface web)

---

## 📊 Monitoramento

### Ver o que o Bot Está Fazendo

**Terminal:**
- O bot mostra mensagens no terminal em tempo real
- Você verá quando detecta tokens
- Você verá quando compra/vende

**Interface Web:**
- Acesse: http://localhost:5000
- Veja tokens detectados
- Veja trades executados
- Veja estatísticas

**Logs:**
- Pasta `logs/` contém logs detalhados
- Arquivo: `logs/bot_YYYYMMDD.log`
- Útil para debug

---

## ✅ Checklist Final

Antes de iniciar o bot, verifique:

- [ ] `TELEGRAM_API_ID` configurado no `.env`
- [ ] `TELEGRAM_API_HASH` configurado no `.env`
- [ ] `TELEGRAM_PHONE` configurado no `.env` (formato: +5511999999999)
- [ ] `TELEGRAM_CHANNEL` configurado no `.env` (ID, nome ou username)
- [ ] Testou conexão com `python testar_telegram.py`
- [ ] Recebeu e digitou o código de verificação
- [ ] Bot consegue encontrar o canal/grupo
- [ ] Bot está "escutando" o canal correto

**Pronto! O bot está configurado para coletar dados do Telegram! 🎉**

---

## 📚 Mais Informações

- **Documentação Telethon**: https://docs.telethon.dev/
- **API do Telegram**: https://core.telegram.org/api
- **my.telegram.org**: https://my.telegram.org/apps

---

**Dúvidas?** Abra uma issue no GitHub ou consulte o README.md principal.




