# 💰 Fontes de Preço em Tempo Real

Este documento explica **quais fontes de preço** o bot usa para acompanhar os tokens em tempo real.

---

## 📊 Fontes de Preço Disponíveis

O bot usa **3 fontes de preço** em ordem de prioridade (com fallback automático):

### 1. 🦅 BirdEye API (Recomendado - Mais Preciso)

**Prioridade**: ⭐⭐⭐⭐⭐ (Primeira opção se configurado)

**Vantagens:**
- ✅ Preços mais precisos e atualizados
- ✅ Suporta tokens novos rapidamente
- ✅ Dados agregados de múltiplas DEXs
- ✅ API estável e confiável

**Desvantagens:**
- ⚠️ Requer API Key (gratuita)
- ⚠️ Tem rate limits (mas generosos)

**Como obter API Key:**
1. Acesse: https://birdeye.so/
2. Crie uma conta (gratuita)
3. Vá em "API" → "Get API Key"
4. Copie a chave
5. Adicione no `.env`: `BIRDEYE_API_KEY=sua_chave_aqui`

**Endpoint usado:**
```
GET https://public-api.birdeye.so/v1/token/price?address={token_address}
Headers: X-API-KEY: sua_chave
```

---

### 2. 🪐 Jupiter Price API (Fallback 1)

**Prioridade**: ⭐⭐⭐⭐ (Segunda opção)

**Vantagens:**
- ✅ Gratuita (sem API key necessária)
- ✅ Dados da própria Jupiter (DEX usada para trading)
- ✅ Atualizações rápidas
- ✅ Confiável

**Desvantagens:**
- ⚠️ Pode não ter preço para tokens muito novos
- ⚠️ Rate limits (mas raramente atingidos)

**Endpoint usado:**
```
GET https://price.jup.ag/v4/price?ids={token_address}
```

**Não requer configuração** - funciona automaticamente!

---

### 3. 📈 DexScreener API (Fallback 2)

**Prioridade**: ⭐⭐⭐ (Última opção)

**Vantagens:**
- ✅ Gratuita (sem API key)
- ✅ Boa cobertura de tokens
- ✅ Dados de múltiplas DEXs

**Desvantagens:**
- ⚠️ Pode ser mais lenta
- ⚠️ Pode não ter todos os tokens

**Endpoint usado:**
```
GET https://api.dexscreener.com/latest/dex/tokens/{token_address}
```

**Não requer configuração** - funciona automaticamente!

---

## 🔄 Como Funciona o Sistema de Fallback

```
1. Tenta BirdEye (se tiver API key)
   ↓ (se falhar ou não tiver key)
2. Tenta Jupiter
   ↓ (se falhar)
3. Tenta DexScreener
   ↓ (se falhar)
4. Retorna None (preço não disponível)
```

**O bot sempre tenta a melhor fonte disponível!**

---

## ⚡ Atualização em Tempo Real

### No Bot (Take Profit Manager)

- **Frequência**: A cada **10 segundos**
- **Fonte**: Usa `PriceMonitor.get_token_price()`
- **Uso**: Monitora tokens comprados para executar take profits

### Na Interface Web

- **Frequência**: A cada **30 segundos** (auto-refresh)
- **Fonte**: API `/api/detected-tokens/<ca>/update-price`
- **Uso**: Atualiza preços na interface para visualização

### Atualização Manual

Você pode atualizar preços manualmente:

1. **Interface Web** → Aba "Detectados"
2. Clique no botão **"Atualizar Preço"** em cada token
3. Ou clique em **"Atualizar Preços"** na aba "Vendidos"

---

## 🎯 Recomendação

### Para Melhor Performance:

1. **Configure BirdEye API** (recomendado):
   ```env
   BIRDEYE_API_KEY=sua_chave_aqui
   ```
   
   **Por quê?**
   - Preços mais precisos
   - Melhor para tokens novos
   - Atualizações mais rápidas

2. **Deixe Jupiter e DexScreener como fallback**:
   - Já funcionam automaticamente
   - Não precisam de configuração
   - Servem como backup

---

## 📊 Comparação das Fontes

| Fonte | Precisão | Velocidade | Tokens Novos | API Key | Rate Limit |
|-------|----------|------------|--------------|---------|------------|
| **BirdEye** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Sim | Generoso |
| **Jupiter** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ Não | Médio |
| **DexScreener** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ❌ Não | Baixo |

---

## 🔧 Configuração

### Mínima (Funciona sem API Key)

```env
# Não precisa configurar nada!
# Jupiter e DexScreener funcionam automaticamente
```

### Recomendada (Com BirdEye)

```env
BIRDEYE_API_KEY=sua_chave_birdeye_aqui
```

**Como obter:**
1. https://birdeye.so/
2. Criar conta (gratuita)
3. API → Get API Key
4. Copiar e colar no `.env`

---

## 🐛 Troubleshooting

### Preços não atualizam

**Possíveis causas:**
1. Token muito novo (ainda não listado nas APIs)
2. Rate limit atingido
3. Problema de conexão

**Soluções:**
- Aguarde alguns minutos (token pode ser muito novo)
- Configure BirdEye API (melhor cobertura)
- Verifique conexão com internet

### Preços mostram $0.00

**Possíveis causas:**
1. Token não encontrado nas APIs
2. Token muito novo
3. Erro na busca

**Soluções:**
- Use atualização manual
- Aguarde alguns minutos
- Verifique se o Contract Address está correto

### Preços diferentes entre fontes

**Normal!** Diferentes APIs podem ter preços ligeiramente diferentes porque:
- Agregam dados de DEXs diferentes
- Têm delays diferentes
- Usam métodos de cálculo diferentes

**O bot usa a melhor fonte disponível!**

---

## 📝 Código de Referência

### Buscar Preço (Python)

```python
from price_monitor import PriceMonitor

monitor = PriceMonitor()
price = await monitor.get_token_price("CONTRACT_ADDRESS")
```

### Atualizar Preço na Interface (JavaScript)

```javascript
// Atualizar preço de um token específico
fetch(`/api/detected-tokens/${contractAddress}/update-price`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
})
```

---

## ✅ Resumo

**Fontes usadas:**
1. 🦅 **BirdEye** (se configurado - melhor)
2. 🪐 **Jupiter** (fallback automático)
3. 📈 **DexScreener** (fallback automático)

**Atualização:**
- Bot: A cada 10 segundos (tokens comprados)
- Interface: A cada 30 segundos (visualização)
- Manual: Botão "Atualizar Preço"

**Recomendação:**
- Configure BirdEye API para melhor performance
- Deixe Jupiter e DexScreener como fallback automático

---

**Dúvidas?** Consulte o README.md ou abra uma issue no GitHub.




