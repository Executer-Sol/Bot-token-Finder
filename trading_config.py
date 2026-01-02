"""
Gerenciador de configurações de trading (TPs e Stop Loss)
Permite ajustar configurações via interface web
"""
import json
import os
from typing import Dict, List

CONFIG_FILE = 'trading_config.json'

# Configurações padrão
DEFAULT_CONFIG = {
    'take_profits': {
        'score_15_17': [
            {'multiple': 2.0, 'sell_percent': 50},
            {'multiple': 4.0, 'sell_percent': 20},
            {'multiple': 8.0, 'sell_percent': 15}
        ],
        'score_18_19': [
            {'multiple': 1.5, 'sell_percent': 50},
            {'multiple': 3.0, 'sell_percent': 50}
        ],
        'score_20_21': [
            {'multiple': 1.5, 'sell_percent': 50},
            {'multiple': 2.5, 'sell_percent': 50}
        ]
    },
    'stop_loss': {
        'time_minutes': 5,
        'min_multiple': 1.0,
        'percent_drop_enabled': False,
        'percent_drop_threshold': 20.0  # Vende se cair 20% do pico
    }
}

def load_config() -> Dict:
    """Carrega configurações do arquivo"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Mescla com padrões para garantir que todas as chaves existam
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                # Mescla take_profits e stop_loss também
                if 'take_profits' in config:
                    merged['take_profits'].update(config['take_profits'])
                if 'stop_loss' in config:
                    merged['stop_loss'].update(config['stop_loss'])
                return merged
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict):
    """Salva configurações no arquivo"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_take_profits_for_score(score: int) -> List[Dict]:
    """Retorna lista de take profits para um score"""
    config = load_config()
    
    if 15 <= score <= 17:
        return config['take_profits'].get('score_15_17', DEFAULT_CONFIG['take_profits']['score_15_17'])
    elif 18 <= score <= 19:
        return config['take_profits'].get('score_18_19', DEFAULT_CONFIG['take_profits']['score_18_19'])
    elif 20 <= score <= 21:
        return config['take_profits'].get('score_20_21', DEFAULT_CONFIG['take_profits']['score_20_21'])
    else:
        return []

def get_stop_loss_config() -> Dict:
    """Retorna configurações de stop loss"""
    config = load_config()
    return config.get('stop_loss', DEFAULT_CONFIG['stop_loss'])

def update_take_profits(score_range: str, tps: List[Dict]):
    """Atualiza take profits para um range de score"""
    config = load_config()
    if 'take_profits' not in config:
        config['take_profits'] = {}
    config['take_profits'][score_range] = tps
    save_config(config)

def update_stop_loss(stop_loss_config: Dict):
    """Atualiza configurações de stop loss"""
    config = load_config()
    config['stop_loss'] = stop_loss_config
    save_config(config)










