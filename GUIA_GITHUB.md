# 🚀 Guia: Como Publicar no GitHub

Este guia explica passo a passo como publicar seu bot no GitHub de forma segura.

## ⚠️ IMPORTANTE: Segurança Antes de Publicar

**NUNCA publique:**
- ❌ Arquivo `.env` (contém chaves privadas)
- ❌ Arquivo `session.session` (sessão do Telegram)
- ❌ Chaves privadas no código
- ❌ API keys no código
- ❌ Dados pessoais

**✅ O que pode publicar:**
- ✅ Código fonte
- ✅ Arquivos de configuração de exemplo (`env.example`)
- ✅ Documentação
- ✅ Scripts de teste

---

## 📋 Passo 1: Verificar Arquivos Sensíveis

### 1.1. Verificar .gitignore

Certifique-se de que o `.gitignore` está configurado corretamente:

```bash
# Verifique se .gitignore existe
cat .gitignore
```

Deve conter pelo menos:
- `.env`
- `session.session`
- `*.key`
- `*.pem`
- Arquivos de dados (trades_history.json, etc)

### 1.2. Verificar se .env está sendo ignorado

```bash
# Verifique se .env está no .gitignore
grep -i "\.env" .gitignore
```

Se não estiver, adicione:
```
.env
.env.local
.env.*.local
```

### 1.3. Verificar código por chaves privadas

```bash
# Procure por padrões suspeitos no código
grep -r "SOLANA_PRIVATE_KEY" --include="*.py" --include="*.js" --include="*.html"
grep -r "sk-" --include="*.py"
grep -r "api_key" --include="*.py" -i
```

**Se encontrar chaves privadas no código:**
1. Remova imediatamente
2. Use variáveis de ambiente (`.env`)
3. Use `env.example` como template

---

## 📦 Passo 2: Preparar Repositório Local

### 2.1. Inicializar Git (se ainda não fez)

```bash
git init
```

### 2.2. Adicionar Arquivos

```bash
# Adicione todos os arquivos (exceto os ignorados)
git add .
```

### 2.3. Verificar o que será commitado

```bash
# Veja o que será commitado (NÃO deve ter .env ou session.session)
git status
```

**Certifique-se de que:**
- ✅ `.env` NÃO aparece na lista
- ✅ `session.session` NÃO aparece na lista
- ✅ Arquivos de dados NÃO aparecem

### 2.4. Fazer Primeiro Commit

```bash
git commit -m "Initial commit: Bot de trading automatizado para Solana"
```

---

## 🌐 Passo 3: Criar Repositório no GitHub

### 3.1. Acessar GitHub

1. Acesse: https://github.com
2. Faça login na sua conta
3. Clique no botão **"+"** no canto superior direito
4. Selecione **"New repository"**

### 3.2. Configurar Repositório

**Nome do repositório:**
- Exemplo: `telegram-trading-bot`
- Ou: `solana-trading-bot`

**Descrição:**
- Exemplo: `Bot automatizado para trading de tokens Solana via Telegram`

**Visibilidade:**
- **Public**: Qualquer um pode ver (recomendado para projetos open source)
- **Private**: Apenas você pode ver (se quiser manter privado)

**Outras opções:**
- ❌ NÃO marque "Add a README file" (você já tem)
- ❌ NÃO marque "Add .gitignore" (você já tem)
- ❌ NÃO marque "Choose a license" (pode adicionar depois)

### 3.3. Criar Repositório

Clique em **"Create repository"**

---

## 🔗 Passo 4: Conectar Repositório Local ao GitHub

### 4.1. Copiar URL do Repositório

No GitHub, você verá uma URL como:
```
https://github.com/SEU_USUARIO/telegram-trading-bot.git
```

### 4.2. Adicionar Remote

```bash
# Substitua SEU_USUARIO e NOME_DO_REPO
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
```

### 4.3. Verificar Remote

```bash
git remote -v
```

Deve mostrar:
```
origin  https://github.com/SEU_USUARIO/NOME_DO_REPO.git (fetch)
origin  https://github.com/SEU_USUARIO/NOME_DO_REPO.git (push)
```

---

## 📤 Passo 5: Enviar Código para GitHub

### 5.1. Renomear Branch (se necessário)

```bash
# GitHub agora usa 'main' ao invés de 'master'
git branch -M main
```

### 5.2. Enviar Código

```bash
git push -u origin main
```

**Na primeira vez, você precisará:**
- Fazer login no GitHub
- Autorizar o Git a acessar sua conta
- Ou usar um token de acesso pessoal

### 5.3. Verificar no GitHub

1. Acesse seu repositório no GitHub
2. Verifique se todos os arquivos foram enviados
3. **IMPORTANTE**: Certifique-se de que `.env` NÃO está lá!

---

## 🔒 Passo 6: Verificação Final de Segurança

### 6.1. Verificar no GitHub

No seu repositório, verifique:

1. **Arquivo `.env` NÃO deve aparecer**
   - Se aparecer, remova imediatamente!
   - Vá em Settings → Secrets → Delete

2. **Arquivo `session.session` NÃO deve aparecer**
   - Se aparecer, remova imediatamente!

3. **Nenhuma chave privada no código**
   - Procure por padrões como: `sk-`, `SOLANA_PRIVATE_KEY=`, etc
   - Se encontrar, remova e faça novo commit

### 6.2. Se Encontrou Informações Sensíveis

**Se você acidentalmente commitou informações sensíveis:**

1. **Remova do histórico:**
```bash
# Remover arquivo do histórico
git rm --cached .env
git commit -m "Remove .env from repository"
git push
```

2. **Se já foi publicado:**
   - Considere as chaves como comprometidas
   - **Gere novas chaves imediatamente**
   - Atualize no `.env` local
   - Use GitHub Secrets para CI/CD (se aplicável)

---

## 📝 Passo 7: Melhorar o Repositório

### 7.1. Adicionar Descrição

No GitHub, vá em:
- Settings → General → Description
- Adicione uma descrição clara

### 7.2. Adicionar Tópicos

Adicione tópicos relevantes:
- `solana`
- `trading-bot`
- `telegram`
- `cryptocurrency`
- `automation`

### 7.3. Adicionar Licença (Opcional)

Crie um arquivo `LICENSE` ou use o GitHub para adicionar.

Opções comuns:
- **MIT**: Permissiva, permite uso comercial
- **Apache 2.0**: Similar ao MIT
- **GPL v3**: Copyleft, código derivado deve ser open source

---

## 🎯 Passo 8: Manter o Repositório Atualizado

### 8.1. Fazer Mudanças

```bash
# Após fazer mudanças no código
git add .
git commit -m "Descrição das mudanças"
git push
```

### 8.2. Criar Releases (Opcional)

1. No GitHub, vá em **Releases**
2. Clique em **"Create a new release"**
3. Defina uma tag (ex: `v1.0.0`)
4. Adicione descrição das mudanças
5. Publique

---

## ✅ Checklist Final

Antes de publicar, verifique:

- [ ] `.env` está no `.gitignore`
- [ ] `session.session` está no `.gitignore`
- [ ] Nenhuma chave privada no código
- [ ] `env.example` existe e está atualizado
- [ ] README.md está completo
- [ ] Documentação está clara
- [ ] Código está limpo e comentado
- [ ] Testou que o repositório não contém dados sensíveis

---

## 🆘 Problemas Comuns

### Erro: "Permission denied"

**Solução:**
- Verifique se você tem permissão no repositório
- Use um token de acesso pessoal
- Configure SSH keys

### Erro: "Repository not found"

**Solução:**
- Verifique a URL do repositório
- Certifique-se de que o repositório existe
- Verifique se você tem acesso

### Acidentalmente commitou .env

**Solução:**
```bash
# Remover do histórico
git rm --cached .env
git commit -m "Remove .env"
git push

# IMPORTANTE: Gere novas chaves!
```

---

## 📚 Recursos Úteis

- **GitHub Docs**: https://docs.github.com/
- **Git Handbook**: https://guides.github.com/introduction/git-handbook/
- **GitHub Security**: https://docs.github.com/en/code-security

---

**Pronto! Seu bot está no GitHub de forma segura! 🎉**

Lembre-se: **Nunca compartilhe suas chaves privadas!**
