"""
Controle de ativação/desativação do bot
"""
import os
import json

BOT_STATE_FILE = 'bot_state.json'

def get_bot_state():
    """Retorna estado atual do bot"""
    if os.path.exists(BOT_STATE_FILE):
        try:
            # Lê o arquivo toda vez (sem cache) para detectar mudanças
            with open(BOT_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return state.get('enabled', True)
        except Exception as e:
            # Em caso de erro, retorna True (ativado por padrão)
            return True
    return True  # Por padrão, ativado

def set_bot_state(enabled: bool):
    """Define estado do bot"""
    with open(BOT_STATE_FILE, 'w') as f:
        json.dump({'enabled': enabled}, f, indent=2)
        f.flush()  # Garante que o arquivo é salvo imediatamente
        os.fsync(f.fileno())  # Força escrita no disco
    return enabled

