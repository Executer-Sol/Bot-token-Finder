"""
Rastreia todos os tokens detectados pelo bot (mesmo que não tenha comprado)
Mantém histórico de preços para análise
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

DETECTED_TOKENS_FILE = 'detected_tokens.json'

def load_detected_tokens() -> Dict:
    """Carrega lista de tokens detectados"""
    if os.path.exists(DETECTED_TOKENS_FILE):
        try:
            with open(DETECTED_TOKENS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'tokens': []}
    return {'tokens': []}

def save_detected_tokens(data: Dict):
    """Salva lista de tokens detectados"""
    with open(DETECTED_TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_detected_token(symbol: str, score: int, price: float, ca: str, 
                       minutes_detected: int = None, detected_at: datetime = None):
    """Adiciona ou atualiza token detectado
    Se o token já existe, não duplica, mas atualiza se necessário
    """
    data = load_detected_tokens()
    tokens = data.get('tokens', [])
    
    # Verifica se já existe
    existing = None
    for token in tokens:
        if token.get('contract_address') == ca:
            existing = token
            break
    
    if detected_at is None:
        detected_at = datetime.now(timezone.utc)
    
    token_data = {
        'symbol': symbol,
        'score': score,
        'initial_price': price,
        'contract_address': ca,
        'minutes_detected': minutes_detected,
        'detected_at': detected_at.isoformat() if isinstance(detected_at, datetime) else detected_at,
        'price_history': [
            {
                'price': price,
                'timestamp': detected_at.isoformat() if isinstance(detected_at, datetime) else detected_at,
                'minutes_since_detection': 0
            }
        ],
        'max_price': price,
        'min_price': price,
        'max_multiple': 1.0,
        'min_multiple': 1.0,
        'current_price': price,
        'current_multiple': 1.0,
        'was_bought': False,
        'last_updated': detected_at.isoformat() if isinstance(detected_at, datetime) else detected_at
    }
    
    if existing:
        # Atualiza apenas se for mais recente ou se não tinha symbol
        existing['last_updated'] = token_data['last_updated']
        if not existing.get('symbol') or existing.get('symbol') == 'N/A':
            existing['symbol'] = symbol
        if existing.get('score') is None:
            existing['score'] = score
    else:
        # Adiciona novo token
        tokens.append(token_data)
    
    # Limita a 1000 tokens mais recentes (evita arquivo muito grande)
    tokens.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
    data['tokens'] = tokens[:1000]
    
    save_detected_tokens(data)
    return token_data

def update_token_price(ca: str, current_price: float):
    """Atualiza preço atual de um token detectado"""
    data = load_detected_tokens()
    tokens = data.get('tokens', [])
    
    for token in tokens:
        if token.get('contract_address') == ca:
            initial_price = token.get('initial_price', current_price)
            if initial_price == 0:
                initial_price = current_price
                token['initial_price'] = current_price
            
            multiple = current_price / initial_price if initial_price > 0 else 1.0
            
            # Atualiza preço atual
            token['current_price'] = current_price
            token['current_multiple'] = multiple
            
            # Atualiza máximo/mínimo
            if current_price > token.get('max_price', current_price):
                token['max_price'] = current_price
                token['max_multiple'] = multiple
            
            if current_price < token.get('min_price', current_price):
                token['min_price'] = current_price
                token['min_multiple'] = multiple
            
            # Adiciona ao histórico (limitado a últimas 100 entradas)
            now = datetime.now(timezone.utc)
            detected_at = datetime.fromisoformat(token.get('detected_at', now.isoformat()).replace('Z', '+00:00'))
            minutes_since = int((now - detected_at).total_seconds() / 60)
            
            price_entry = {
                'price': current_price,
                'timestamp': now.isoformat(),
                'minutes_since_detection': minutes_since
            }
            
            history = token.get('price_history', [])
            history.append(price_entry)
            # Mantém apenas últimas 100 entradas
            token['price_history'] = history[-100:]
            token['last_updated'] = now.isoformat()
            
            save_detected_tokens(data)
            return token
    
    return None

def mark_token_as_bought(ca: str):
    """Marca token como comprado"""
    data = load_detected_tokens()
    tokens = data.get('tokens', [])
    
    for token in tokens:
        if token.get('contract_address') == ca:
            token['was_bought'] = True
            save_detected_tokens(data)
            return token
    
    return None

def get_all_detected_tokens(limit: int = 100) -> List[Dict]:
    """Retorna lista de tokens detectados (mais recentes primeiro)"""
    data = load_detected_tokens()
    tokens = data.get('tokens', [])
    
    # Ordena por data de detecção (mais recentes primeiro)
    tokens.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
    
    return tokens[:limit]





