"""
Script para verificar se o bot está vendo tokens
"""
import os
import json
from datetime import datetime

print("="*60)
print("VERIFICAÇÃO DO BOT")
print("="*60)

# Verifica se o arquivo existe
if os.path.exists('last_token_detected.json'):
    with open('last_token_detected.json', 'r', encoding='utf-8') as f:
        token = json.load(f)
    
    print("\nBOT ESTA VENDO TOKENS!")
    print("\nÚltimo token que o bot VIU:")
    print("-"*60)
    print(f"Símbolo: {token.get('symbol', 'N/A')}")
    print(f"Score: {token.get('score', 'N/A')}")
    print(f"Preço: ${token.get('price', 'N/A')}")
    print(f"Contract Address: {token.get('contract_address', 'N/A')}")
    print(f"Minutos desde detecção: {token.get('minutes_detected', 'N/A')}")
    print(f"Detectado em: {token.get('detected_at', 'N/A')}")
    
    # Verifica se comprou
    if os.path.exists('trades_history.json'):
        with open('trades_history.json', 'r', encoding='utf-8') as f:
            trades = json.load(f)
        
        ca = token.get('contract_address')
        comprado = False
        for trade in trades.get('active', []) + trades.get('sold', []):
            if trade.get('contract_address') == ca:
                comprado = True
                print(f"\nStatus: COMPROU este token")
                break
        
        if not comprado:
            print(f"\nStatus: VIU mas NAO comprou (fora da janela de tempo ou bot desativado)")
else:
    print("\nBOT AINDA NAO VIU NENHUM TOKEN")
    print("\nPossíveis motivos:")
    print("1. Bot não está rodando")
    print("2. Bot não está conectado ao Telegram")
    print("3. Bot não recebeu mensagens ainda")
    print("4. Canal do Telegram não configurado corretamente")

print("\n" + "="*60)

