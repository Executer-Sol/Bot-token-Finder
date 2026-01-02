"""
Sistema de blacklist de tokens (lookup O(1) - muito rápido)
"""
import os
import json
from pathlib import Path

BLACKLIST_FILE = 'token_blacklist.json'

def load_blacklist():
    """Carrega blacklist do arquivo (muito rápido - apenas leitura)"""
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                data = json.load(f)
                # Converte para set para lookup O(1)
                return set(data.get('addresses', []))
        except:
            return set()
    return set()

def save_blacklist(blacklist_set):
    """Salva blacklist (só quando adiciona/remove - não durante compra)"""
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump({'addresses': list(blacklist_set)}, f, indent=2)

def is_blacklisted(contract_address: str) -> bool:
    """Verifica se token está na blacklist (O(1) - instantâneo)"""
    blacklist = load_blacklist()
    return contract_address in blacklist

def add_to_blacklist(contract_address: str):
    """Adiciona token à blacklist"""
    blacklist = load_blacklist()
    blacklist.add(contract_address)
    save_blacklist(blacklist)

def remove_from_blacklist(contract_address: str):
    """Remove token da blacklist"""
    blacklist = load_blacklist()
    blacklist.discard(contract_address)
    save_blacklist(blacklist)

# Cache da blacklist (carrega uma vez, atualiza quando necessário)
_blacklist_cache = None

def get_blacklist_cache():
    """Retorna cache da blacklist (muito rápido)"""
    global _blacklist_cache
    if _blacklist_cache is None:
        _blacklist_cache = load_blacklist()
    return _blacklist_cache

def refresh_blacklist_cache():
    """Atualiza cache (chamar quando adiciona/remove)"""
    global _blacklist_cache
    _blacklist_cache = load_blacklist()











