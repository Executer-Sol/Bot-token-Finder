import os
from dotenv import load_dotenv

load_dotenv()

# Telegram (opcional - pode ser substituído pela Gangue)
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_CHANNEL = os.getenv('TELEGRAM_CHANNEL')

# Gangue (fonte alternativa de tokens - mais rápida)
# IMPORTANTE: Para usar Telegram, defina USE_GANGUE=false no .env ou deixe sem definir
USE_GANGUE = os.getenv('USE_GANGUE', '').lower() == 'true'  # Só usa Gangue se explicitamente 'true'
GANGUE_COOKIES_FILE = os.getenv('GANGUE_COOKIES_FILE', 'cookies.json')  # Arquivo com cookies (padrão: cookies.json)
GANGUE_SESSION_COOKIE = os.getenv('GANGUE_SESSION_COOKIE', '')  # Cookie de sessão (opcional se usar arquivo)
GANGUE_GA_COOKIE = os.getenv('GANGUE_GA_COOKIE', '')  # Cookie do Google Analytics (opcional se usar arquivo)
GANGUE_POLL_INTERVAL = int(os.getenv('GANGUE_POLL_INTERVAL', '5'))  # Intervalo de polling em segundos

# Solana
SOLANA_PRIVATE_KEY = os.getenv('SOLANA_PRIVATE_KEY')
RPC_URL = os.getenv('RPC_URL', 'https://api.mainnet-beta.solana.com')  # Use Alchemy RPC para melhor performance

# API Keys (opcional)
BIRDEYE_API_KEY = os.getenv('BIRDEYE_API_KEY', '')  # Opcional: https://birdeye.so
JUPITER_API_KEY = os.getenv('JUPITER_API_KEY', '')  # Opcional: Para reduzir rate limits

# Trading
SLIPPAGE_BPS = int(os.getenv('SLIPPAGE_BPS', '1000'))  # 10% padrão (1000 bps = 10%)
MIN_SCORE = int(os.getenv('MIN_SCORE', '15'))
MAX_SCORE = int(os.getenv('MAX_SCORE', '21'))

# Limite de perda diário (em SOL) - opcional
# Se configurado, bot para de comprar quando atingir limite
MAX_DAILY_LOSS_SOL = float(os.getenv('MAX_DAILY_LOSS_SOL', '0'))  # 0 = sem limite

# Valores por Score (em SOL) - Alocação ideal
# Score 15-17: 0.05 SOL (aproximadamente $5 USD)
AMOUNT_SOL_15_17 = float(os.getenv('AMOUNT_SOL_15_17', '0.05'))
# Score 18-19: 0.03 SOL (aproximadamente $3 USD)
AMOUNT_SOL_18_19 = float(os.getenv('AMOUNT_SOL_18_19', '0.03'))
# Score 20-21: 0.02 SOL (aproximadamente $2 USD)
AMOUNT_SOL_20_21 = float(os.getenv('AMOUNT_SOL_20_21', '0.02'))
# Score <15: 0.01 SOL (aproximadamente $1 USD) ou ignorar
AMOUNT_SOL_LOW = float(os.getenv('AMOUNT_SOL_LOW', '0.01'))
ENABLE_LOW_SCORE = os.getenv('ENABLE_LOW_SCORE', 'false').lower() == 'true'

# Tempo máximo para compra (em minutos) - Regra de timing
# Score 15-17: máximo 3 minutos (tokens explodem rápido)
MAX_TIME_MINUTES_15_17 = int(os.getenv('MAX_TIME_MINUTES_15_17', '3'))
# Score 18-19: máximo 5 minutos
MAX_TIME_MINUTES_18_19 = int(os.getenv('MAX_TIME_MINUTES_18_19', '5'))
# Score 20-21: só se imediato (0 minutos = primeiro minuto)
MAX_TIME_MINUTES_20_21 = int(os.getenv('MAX_TIME_MINUTES_20_21', '1'))

# Stop Loss por Tempo - Se token não subir em X minutos, vende tudo
# Baseado na média: tokens que dão certo começam a subir em 1-5 minutos
# Se não subiu em 5 minutos, provavelmente não vai subir
STOP_LOSS_TIME_MINUTES = int(os.getenv('STOP_LOSS_TIME_MINUTES', '5'))  # 5 minutos padrão
STOP_LOSS_MIN_MULTIPLE = float(os.getenv('STOP_LOSS_MIN_MULTIPLE', '1.0'))  # Múltiplo mínimo esperado (1.0 = não caiu)

# Take Profit Score 15-17
TP1_MULTIPLE = float(os.getenv('TP1_MULTIPLE', '2'))
TP1_SELL_PERCENT = float(os.getenv('TP1_SELL_PERCENT', '50'))
TP2_MULTIPLE = float(os.getenv('TP2_MULTIPLE', '4'))
TP2_SELL_PERCENT = float(os.getenv('TP2_SELL_PERCENT', '20'))
TP3_MULTIPLE = float(os.getenv('TP3_MULTIPLE', '8'))
TP3_SELL_PERCENT = float(os.getenv('TP3_SELL_PERCENT', '15'))

# Take Profit Score 18-19
TP1_MULTIPLE_18_19 = float(os.getenv('TP1_MULTIPLE_18_19', '1.5'))
TP1_SELL_PERCENT_18_19 = float(os.getenv('TP1_SELL_PERCENT_18_19', '50'))
TP2_MULTIPLE_18_19 = float(os.getenv('TP2_MULTIPLE_18_19', '3'))
TP2_SELL_PERCENT_18_19 = float(os.getenv('TP2_SELL_PERCENT_18_19', '50'))

# Take Profit Score 20-21
TP1_MULTIPLE_20_21 = float(os.getenv('TP1_MULTIPLE_20_21', '1.5'))
TP1_SELL_PERCENT_20_21 = float(os.getenv('TP1_SELL_PERCENT_20_21', '50'))
TP2_MULTIPLE_20_21 = float(os.getenv('TP2_MULTIPLE_20_21', '2.5'))
TP2_SELL_PERCENT_20_21 = float(os.getenv('TP2_SELL_PERCENT_20_21', '50'))

def get_amount_by_score(score: int) -> float:
    """Retorna o valor em SOL baseado no score"""
    if 15 <= score <= 17:
        return AMOUNT_SOL_15_17
    elif 18 <= score <= 19:
        return AMOUNT_SOL_18_19
    elif 20 <= score <= 21:
        return AMOUNT_SOL_20_21
    elif score < 15:
        return AMOUNT_SOL_LOW if ENABLE_LOW_SCORE else 0
    else:
        return 0

def get_max_time_by_score(score: int) -> int:
    """Retorna o tempo máximo em minutos para compra baseado no score"""
    if 15 <= score <= 17:
        return MAX_TIME_MINUTES_15_17
    elif 18 <= score <= 19:
        return MAX_TIME_MINUTES_18_19
    elif 20 <= score <= 21:
        return MAX_TIME_MINUTES_20_21
    else:
        return 0  # Não compra se não tem regra definida

def reload_config():
    """Recarrega configurações do .env (útil quando valores são atualizados via interface web)"""
    global AMOUNT_SOL_15_17, AMOUNT_SOL_18_19, AMOUNT_SOL_20_21, AMOUNT_SOL_LOW
    global ENABLE_LOW_SCORE
    global MAX_TIME_MINUTES_15_17, MAX_TIME_MINUTES_18_19, MAX_TIME_MINUTES_20_21
    
    # Recarrega valores do .env
    load_dotenv(override=True)  # override=True força recarregar
    
    AMOUNT_SOL_15_17 = float(os.getenv('AMOUNT_SOL_15_17', '0.05'))
    AMOUNT_SOL_18_19 = float(os.getenv('AMOUNT_SOL_18_19', '0.03'))
    AMOUNT_SOL_20_21 = float(os.getenv('AMOUNT_SOL_20_21', '0.02'))
    AMOUNT_SOL_LOW = float(os.getenv('AMOUNT_SOL_LOW', '0.01'))
    ENABLE_LOW_SCORE = os.getenv('ENABLE_LOW_SCORE', 'false').lower() == 'true'
    MAX_TIME_MINUTES_15_17 = int(os.getenv('MAX_TIME_MINUTES_15_17', '3'))
    MAX_TIME_MINUTES_18_19 = int(os.getenv('MAX_TIME_MINUTES_18_19', '5'))
    MAX_TIME_MINUTES_20_21 = int(os.getenv('MAX_TIME_MINUTES_20_21', '1'))

