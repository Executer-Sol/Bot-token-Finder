# 🔧 Como Configurar a Gangue

## 📋 Passo a Passo

### 1. Obter os Cookies (Método Automático - Recomendado)

1. **Abra o site:** https://gangue.macaco.club
2. **Faça login** com sua conta
3. **Abra o Console do Navegador:**
   - Pressione **F12** ou **Ctrl + Shift + I**
   - Ou clique com botão direito → **Inspecionar**
   - Vá para a aba **"Console"**
4. **Cole e execute este código:**
```javascript
// Copie TUDO (incluindo as aspas)
copy(JSON.stringify(document.cookie.split('; ').map(c => {
  const [name, ...rest] = c.split('=');
  return {
    name,
    value: rest.join('='),
    domain: '.gangue.macaco.club',
    path: '/'
  };
}), null, 2));
```
5. **Os cookies foram copiados!** Você verá uma mensagem: `undefined` (é normal)
6. **Cole no arquivo `cookies.json`:**
   - Crie o arquivo `cookies.json` na raiz do projeto
   - Cole o conteúdo copiado (Ctrl + V)
   - Salve o arquivo

**⚠️ Nota:** Os erros no console sobre `ethereum`, `MetaMask`, `Backpack`, etc. são normais e não afetam a obtenção dos cookies. São apenas conflitos entre extensões de carteira.

### 2. Formato do arquivo `cookies.json`

O arquivo deve ter este formato:

```json
[
  {
    "name": "session",
    "value": "s%3A1234567890abcdef...",
    "domain": ".gangue.macaco.club",
    "path": "/"
  },
  {
    "name": "_ga",
    "value": "GA1.2.1234567890.1234567890",
    "domain": ".gangue.macaco.club",
    "path": "/"
  }
]
```

### 3. Configurar no `.env` (Opcional)

Se preferir usar variáveis de ambiente em vez do arquivo `cookies.json`:

```env
# Gangue (fonte de tokens - mais rápida que Telegram)
USE_GANGUE=true
GANGUE_COOKIES_FILE=cookies.json
GANGUE_POLL_INTERVAL=5
```

**Onde:**
- `USE_GANGUE=true` - Ativa o uso da Gangue (em vez do Telegram)
- `GANGUE_COOKIES_FILE=cookies.json` - Arquivo com cookies (padrão: cookies.json)
- `GANGUE_POLL_INTERVAL=5` - Intervalo de verificação em segundos (padrão: 5s)

**Nota:** Se você criar o arquivo `cookies.json`, não precisa configurar `GANGUE_SESSION_COOKIE` e `GANGUE_GA_COOKIE` no `.env`. O bot vai ler automaticamente do arquivo.

### 4. Testar

Após configurar, execute:

```bash
python gangue_bot.py
```

Ou use o `run_all.py` que detecta automaticamente:

```bash
python run_all.py
```

## 🔍 Verificar se está funcionando

O bot vai tentar diferentes endpoints da API:
- `/api/tokens`
- `/api/tokens/recent`
- `/api/tokens/latest`
- `/tokens`
- `/api/v1/tokens`

Se nenhum funcionar, ele tenta fazer scraping HTML da página principal.

## ⚠️ Notas

- Os cookies podem expirar. Se o bot parar de funcionar, atualize os cookies.
- O intervalo de polling padrão é 5 segundos. Ajuste conforme necessário.
- Se preferir usar Telegram, configure `USE_GANGUE=false` no `.env`

