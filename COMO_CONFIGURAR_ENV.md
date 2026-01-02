# Como Configurar o arquivo .env

## ⚠️ IMPORTANTE - SEGURANÇA

**NUNCA compartilhe suas chaves privadas!**
- Se você já compartilhou, considere a carteira comprometida
- Crie uma nova carteira para uso real
- Use apenas carteiras de teste para desenvolvimento

## Configuração do .env

Crie um arquivo `.env` na raiz do projeto com:

```env
# Telegram
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=+5511999999999
TELEGRAM_CHANNEL=nome_do_canal

# Solana
SOLANA_PRIVATE_KEY=sua_chave_privada_base58
RPC_URL=https://api.mainnet-beta.solana.com

# API Keys (opcional)
BIRDEYE_API_KEY=
JUPITER_API_KEY=

# Trading
SLIPPAGE_BPS=500
MIN_SCORE=15
MAX_SCORE=21
AMOUNT_USDC_15_17=5.0
AMOUNT_USDC_18_19=3.0
AMOUNT_USDC_20_21=2.0
AMOUNT_USDC_LOW=1.0
ENABLE_LOW_SCORE=false
MAX_TIME_MINUTES_15_17=3
MAX_TIME_MINUTES_18_19=5
MAX_TIME_MINUTES_20_21=1
```

## Formato da Chave Privada

A `SOLANA_PRIVATE_KEY` pode estar em:
- Base58 (88 caracteres): `5vr6Qtd51emaeg5CxoZm7z2W3huFLY18se2g1cL1LY2ZHFyW4YEQik19CJgpNnVVnZEJfgm9V51LYr31KwpTTgDN`
- Base64 (44 caracteres)
- Hex (64 ou 128 caracteres)

O código detecta automaticamente o formato.

## ⚠️ AVISO

**NÃO coloque valores reais de produção aqui!**
Use apenas para testes com valores pequenos!

