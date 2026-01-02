"""
Sistema de limite de perda diário (cálculo rápido)
"""
import os
import json
from datetime import datetime, date
from pathlib import Path
from typing import Tuple, Dict

DAILY_LOSS_FILE = 'daily_loss.json'

def get_daily_stats():
    """Retorna estatísticas do dia atual (cálculo rápido)"""
    today = date.today().isoformat()
    
    if os.path.exists(DAILY_LOSS_FILE):
        try:
            with open(DAILY_LOSS_FILE, 'r') as f:
                data = json.load(f)
                if data.get('date') == today:
                    return data
        except:
            pass
    
    # Novo dia - inicializa
    return {
        'date': today,
        'total_loss': 0.0,
        'total_profit': 0.0,
        'trades_count': 0
    }

def save_daily_stats(stats):
    """Salva estatísticas (rápido)"""
    with open(DAILY_LOSS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def add_trade_result(profit_loss: float):
    """Adiciona resultado de um trade (rápido - apenas soma)"""
    stats = get_daily_stats()
    stats['trades_count'] += 1
    
    if profit_loss > 0:
        stats['total_profit'] += profit_loss
    else:
        stats['total_loss'] += abs(profit_loss)
    
    save_daily_stats(stats)
    return stats

def check_daily_loss_limit(max_loss_sol: float = None) -> Tuple[bool, Dict]:
    """
    Verifica se atingiu limite de perda diário
    Retorna: (limite_atingido, stats)
    Muito rápido - apenas leitura e comparação
    """
    if max_loss_sol is None:
        # Se não configurado, não limita
        return False, get_daily_stats()
    
    stats = get_daily_stats()
    net_loss = stats['total_loss'] - stats['total_profit']
    
    if net_loss >= max_loss_sol:
        return True, stats
    
    return False, stats

def reset_daily_stats():
    """Reseta estatísticas (para novo dia ou manual)"""
    stats = {
        'date': date.today().isoformat(),
        'total_loss': 0.0,
        'total_profit': 0.0,
        'trades_count': 0
    }
    save_daily_stats(stats)
    return stats

