# 🚀 Guia Simples: Como Usar Git e GitHub

## 📚 O Que É Git e GitHub?

- **Git**: Sistema que controla versões do seu código (como um "histórico" de mudanças)
- **GitHub**: Site onde você guarda seu código na nuvem (como um "Google Drive" para código)

---

## 🎯 Como Funciona?

### 1️⃣ **Você Melhora o Código Localmente**
- Você edita arquivos no seu computador
- **NÃO atualiza automaticamente no GitHub!**
- Você precisa "enviar" as mudanças manualmente

### 2️⃣ **Você Envia para o GitHub**
- Usa comandos Git para "enviar" suas mudanças
- Outras pessoas podem ver suas melhorias
- Você tem um backup na nuvem

### 3️⃣ **Se Alguém Mudar no GitHub**
- Você precisa "baixar" as mudanças
- Git ajuda a combinar suas mudanças com as deles
- Pode haver conflitos (quando duas pessoas mudam a mesma coisa)

---

## 📝 Passo a Passo: Primeira Vez no GitHub

### **Passo 1: Criar Conta no GitHub**
1. Acesse: https://github.com
2. Clique em "Sign up"
3. Crie sua conta (grátis)

### **Passo 2: Instalar Git no Seu Computador**

**Windows:**
1. Baixe: https://git-scm.com/download/win
2. Instale (clique "Next" em tudo)
3. Abra o PowerShell ou CMD

**Verificar se instalou:**
```bash
git --version
```
Deve aparecer algo como: `git version 2.xx.x`

### **Passo 3: Configurar Git (Só Uma Vez)**
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

### **Passo 4: Criar Repositório no GitHub**
1. Acesse: https://github.com
2. Clique no botão **"+"** (canto superior direito)
3. Clique em **"New repository"**
4. Preencha:
   - **Repository name**: `telegram-trading-bot` (ou outro nome)
   - **Description**: "Bot de trading para Telegram"
   - Marque **"Public"** (para outros verem) ou **"Private"** (só você)
5. **NÃO marque** "Add a README file" (já temos)
6. Clique em **"Create repository"**

### **Passo 5: Conectar Seu Projeto ao GitHub**

Abra o PowerShell/CMD na pasta do projeto e execute:

```bash
# 1. Inicializar Git (só uma vez)
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Fazer primeiro "commit" (salvar estado)
git commit -m "Primeira versão do bot"

# 4. Conectar ao GitHub (substitua SEU_USUARIO pelo seu nome de usuário)
git remote add origin https://github.com/SEU_USUARIO/telegram-trading-bot.git

# 5. Enviar para o GitHub
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE:** Na primeira vez, o GitHub vai pedir seu usuário e senha (ou token de acesso).

---

## 🔄 Como Atualizar Quando Você Melhorar o Código

**Sempre que você melhorar algo, faça isso:**

```bash
# 1. Ver o que mudou
git status

# 2. Adicionar arquivos modificados
git add .

# 3. Salvar com uma mensagem explicando o que mudou
git commit -m "Adicionei função de venda parcial"

# 4. Enviar para o GitHub
git push
```

**Exemplo de mensagens de commit:**
- `"Corrigido bug na venda manual"`
- `"Adicionada aba de análise de performance"`
- `"Melhorada interface do dashboard"`
- `"Atualizado README com novas instruções"`

---

## 📥 Como Baixar Mudanças de Outras Pessoas

Se alguém mudou algo no GitHub e você quer pegar essas mudanças:

```bash
# Baixar mudanças do GitHub
git pull
```

**Se houver conflitos:**
- Git vai avisar quais arquivos têm conflito
- Você precisa abrir esses arquivos e resolver manualmente
- Depois faça: `git add .` → `git commit -m "Resolvido conflitos"` → `git push`

---

## 🔐 Autenticação no GitHub (Token de Acesso)

GitHub não aceita mais senha normal. Você precisa criar um **Personal Access Token**:

### **Como Criar Token:**

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Dê um nome: `Meu Bot Trading`
4. Marque: **`repo`** (acesso completo aos repositórios)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (você só vê uma vez!)

### **Usar o Token:**

Quando o Git pedir senha:
- **Usuário**: seu nome de usuário do GitHub
- **Senha**: cole o token que você copiou

**Ou configure para salvar:**
```bash
git config --global credential.helper wincred
```

---

## 📋 Comandos Git Mais Usados

```bash
# Ver status (o que mudou)
git status

# Ver histórico de commits
git log

# Ver diferenças (o que mudou nos arquivos)
git diff

# Desfazer mudanças não salvas
git checkout -- nome-do-arquivo.py

# Ver versões anteriores
git log --oneline
git checkout CODIGO_DO_COMMIT  # Voltar para versão antiga
git checkout main              # Voltar para versão atual
```

---

## ⚠️ Dicas Importantes

### ✅ **SEMPRE FAÇA ANTES DE PUSH:**
1. Teste seu código
2. Verifique se não quebrou nada
3. Escreva uma mensagem clara no commit

### ✅ **ANTES DE FAZER MUDANÇAS GRANDES:**
```bash
# Criar uma "cópia" para testar
git checkout -b nome-da-nova-funcionalidade

# Trabalhar normalmente...
git add .
git commit -m "Nova funcionalidade"

# Quando estiver pronto, voltar para main
git checkout main
git merge nome-da-nova-funcionalidade
git push
```

### ✅ **NÃO COMITE:**
- Arquivos `.env` (tem suas chaves privadas!)
- Arquivos `session.session` (sessão do Telegram)
- Arquivos `*.json` com dados pessoais
- Arquivos `__pycache__/` (código compilado)

**Esses arquivos já estão no `.gitignore`! ✅**

---

## 🆘 Problemas Comuns

### **"fatal: not a git repository"**
```bash
# Você não está na pasta do projeto
cd C:\Users\je222\telegram_trading_bot
```

### **"error: failed to push"**
```bash
# Alguém mudou algo no GitHub, baixe primeiro
git pull
# Resolva conflitos se houver
git push
```

### **"error: Your branch is ahead"**
```bash
# Você tem commits locais que não foram enviados
git push
```

### **"error: Authentication failed"**
- Verifique se criou o token de acesso
- Use o token como senha (não sua senha do GitHub)

---

## 📚 Resumo Rápido

**Primeira vez:**
```bash
git init
git add .
git commit -m "Primeira versão"
git remote add origin https://github.com/SEU_USUARIO/nome-do-repo.git
git push -u origin main
```

**Sempre que melhorar:**
```bash
git add .
git commit -m "O que você melhorou"
git push
```

**Para pegar mudanças:**
```bash
git pull
```

---

## 🎓 Aprender Mais

- **Documentação oficial**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com
- **Tutorial interativo**: https://learngitbranching.js.org

---

## ✅ Checklist Antes de Publicar

- [ ] Removido arquivo `.env` (já está no `.gitignore`)
- [ ] Removido `session.session` (já está no `.gitignore`)
- [ ] Verificado que `env.example` existe (para outros copiarem)
- [ ] README.md está atualizado
- [ ] Código testado e funcionando
- [ ] Commit com mensagem clara
- [ ] Push feito com sucesso

---

**🎉 Pronto! Agora você sabe como usar Git e GitHub!**

