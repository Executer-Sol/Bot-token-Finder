"""
Armazena o último token detectado pelo bot (mesmo se desativado)
"""
import json
import os
from datetime import datetime

LAST_TOKEN_FILE = 'last_token_detected.json'

def save_last_token(symbol: str, score: int, price: float, ca: str, minutes_detected: int = None, detected_at = None):
    """Salva último token detectado
    Args:
        detected_at: datetime object com horário de detecção (opcional)
    """
    data = {
        'symbol': symbol,
        'score': score,
        'price': price,
        'contract_address': ca,
        'minutes_detected': minutes_detected,
        'detected_at': detected_at.isoformat() if detected_at else datetime.now().isoformat()
    }
    with open(LAST_TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_last_token():
    """Retorna último token detectado"""
    if os.path.exists(LAST_TOKEN_FILE):
        try:
            with open(LAST_TOKEN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


