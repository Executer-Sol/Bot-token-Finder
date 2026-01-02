# 🤖 Bot de Trading Automatizado para Solana

Bot automatizado que monitora canais do Telegram em busca de novos tokens Solana e executa compras/vendas automaticamente baseado em estratégias configuráveis.

## ⚠️ AVISO IMPORTANTE

**Este bot opera com dinheiro real. Use por sua conta e risco!**

- ⚠️ Sempre use uma carteira SEPARADA apenas para o bot
- ⚠️ Nunca compartilhe sua chave privada
- ⚠️ Comece com valores pequenos para testar
- ⚠️ Trading de criptomoedas envolve risco de perda total

## 🚀 Funcionalidades

- ✅ Monitoramento automático de canais Telegram
- ✅ Compra automática baseada em score do token
- ✅ Take Profit escalonado (vendas parciais)
- ✅ Stop Loss por tempo
- ✅ Interface web para monitoramento e controle
- ✅ Análise de performance detalhada
- ✅ Blacklist de tokens
- ✅ Limite de perda diário
- ✅ Compra e venda manual via interface web

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no Telegram
- Carteira Solana com SOL para trading
- RPC da Solana (recomendado: Alchemy)

## 📦 Instalação

Siga o guia completo de instalação: [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md)

### Passos Rápidos:

1. **Clone o repositório:**
```bash
git clone https://github.com/SEU_USUARIO/telegram_trading_bot.git
cd telegram_trading_bot
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o arquivo `.env`:**
```bash
cp env.example .env
# Edite o .env com suas informações
```

4. **Configure o Telegram:**
Siga o guia: [GUIA_TELEGRAM.md](GUIA_TELEGRAM.md)

5. **Inicie o bot:**
```bash
python bot.py
```

6. **Acesse a interface web:**
Abra no navegador: http://localhost:5000

## 📚 Documentação

- **[GUIA_COMPLETO_LEIGOS.md](GUIA_COMPLETO_LEIGOS.md)** ⭐ **COMECE AQUI!** - Guia completo e simples para iniciantes
- **[GUIA_INSTALACAO.md](GUIA_INSTALACAO.md)** - Instalação passo a passo completa
- **[GUIA_TELEGRAM.md](GUIA_TELEGRAM.md)** - Como configurar o Telegram
- **[FUNCIONALIDADES.md](FUNCIONALIDADES.md)** - Explicação técnica de cada aba e função
- **[GUIA_GIT_SIMPLES.md](GUIA_GIT_SIMPLES.md)** - Como usar Git e GitHub (para iniciantes)
- **[GUIA_GITHUB.md](GUIA_GITHUB.md)** - Como publicar no GitHub

## 🎯 Como Funciona

1. **Monitoramento:** Bot monitora canal do Telegram em tempo real
2. **Detecção:** Quando detecta novo token, analisa score e valida regras
3. **Compra:** Se atender critérios, compra automaticamente via Jupiter
4. **Monitoramento:** Acompanha preço do token a cada 10 segundos
5. **Take Profit:** Vende parcialmente quando atinge múltiplos configurados
6. **Stop Loss:** Vende tudo se token não subir em X minutos

## ⚙️ Configuração

Todas as configurações estão no arquivo `.env`. Principais:

- **Valores por Score:** Quanto investir em cada token (baseado no score)
- **Take Profit:** Múltiplos e percentuais de venda
- **Stop Loss:** Tempo máximo antes de vender
- **Limite Diário:** Limite de perda diário

Veja `env.example` para todas as opções.

## 📊 Interface Web

Acesse http://localhost:5000 para:

- ✅ Ver tokens ativos e vendidos
- ✅ Controlar bot (ativar/desativar)
- ✅ Ajustar valores de compra
- ✅ Ver análise de performance
- ✅ Comprar/vender tokens manualmente
- ✅ Gerenciar blacklist

Veja [FUNCIONALIDADES.md](FUNCIONALIDADES.md) para detalhes de cada aba.

## 🔒 Segurança

- ✅ Chave privada fica apenas no arquivo `.env` (não commitado)
- ✅ Use carteira separada apenas para o bot
- ✅ Nunca compartilhe sua chave privada
- ✅ Revise todas as configurações antes de iniciar

## 🐛 Problemas Comuns

### Bot não conecta ao Telegram
- Verifique `TELEGRAM_API_ID` e `TELEGRAM_API_HASH` no `.env`
- Certifique-se que o número de telefone está correto
- Veja [GUIA_TELEGRAM.md](GUIA_TELEGRAM.md)

### Erro "database is locked"
- Feche outras instâncias do bot
- Execute `PARAR_BOT_ANTES_RODAR.bat` (Windows)
- Remova `session.session-journal` se existir

### Bot não compra tokens
- Verifique se bot está ativado na interface web
- Confirme que tem SOL suficiente na carteira
- Verifique se token não está na blacklist
- Veja logs no terminal para mais detalhes

## 📝 Licença

Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## ⚠️ Disclaimer

Este bot é uma ferramenta educacional. Trading de criptomoedas envolve risco significativo. O desenvolvedor não se responsabiliza por perdas financeiras. Use por sua conta e risco.
