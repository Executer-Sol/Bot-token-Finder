# 📱 Configurar Telegram

Para voltar a usar o Telegram como fonte de tokens:

## 1. Configurar variáveis de ambiente

Crie ou edite o arquivo `.env` na raiz do projeto:

```env
# Telegram
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=seu_telefone_com_codigo_pais
TELEGRAM_CHANNEL=smart
# ou use o ID do chat:
# TELEGRAM_CHANNEL=0eSIqafAvoXvpVQ

# IMPORTANTE: Desativar Gangue
USE_GANGUE=false
```

## 2. Verificar configuração

O bot vai procurar o canal de duas formas:
- Por nome: `smart`
- Por ID: `0eSIqafAvoXvpVQ`
- Por username: `@smart` (se for público)

## 3. Reiniciar o bot

```bash
python run_all.py
```

O bot agora vai usar o Telegram em vez da Gangue!










