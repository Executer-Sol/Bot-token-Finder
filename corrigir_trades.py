"""
Script para corrigir valores em trades_history.json
Converte amount_usdc de SOL para USDC (multiplica por 100)
"""
import json
import os
import sys
import io

# Configura encoding para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TRADES_FILE = 'trades_history.json'
SOL_TO_USD_RATE = 100.0  # 1 SOL ≈ $100

def corrigir_trades():
    """Corrige valores de SOL para USDC no arquivo de trades"""
    if not os.path.exists(TRADES_FILE):
        print(f"Arquivo {TRADES_FILE} não encontrado")
        return
    
    with open(TRADES_FILE, 'r', encoding='utf-8') as f:
        trades = json.load(f)
    
    corrigidos = 0
    
    # Corrige trades ativos
    for trade in trades.get('active', []):
        if trade.get('amount_usdc', 0) < 1.0:  # Se for menor que 1, provavelmente está em SOL
            old_value = trade['amount_usdc']
            trade['amount_usdc'] = old_value * SOL_TO_USD_RATE
            print(f"[OK] Corrigido {trade['symbol']}: {old_value} SOL -> ${trade['amount_usdc']:.2f} USDC")
            corrigidos += 1
    
    # Corrige trades vendidos
    for trade in trades.get('sold', []):
        if trade.get('amount_usdc', 0) < 1.0:  # Se for menor que 1, provavelmente está em SOL
            old_value = trade['amount_usdc']
            trade['amount_usdc'] = old_value * SOL_TO_USD_RATE
            
            # Recalcula valores derivados
            if 'final_value_usdc' in trade:
                final_multiple = trade.get('final_price', 0) / trade.get('entry_price', 1)
                trade['final_value_usdc'] = trade['amount_usdc'] * final_multiple * (trade.get('total_sold_percent', 100) / 100)
                trade['profit_loss_usdc'] = trade['final_value_usdc'] - (trade['amount_usdc'] * (trade.get('total_sold_percent', 100) / 100))
            
            print(f"[OK] Corrigido {trade['symbol']} (vendido): {old_value} SOL -> ${trade['amount_usdc']:.2f} USDC")
            corrigidos += 1
    
    if corrigidos > 0:
        # Salva arquivo corrigido
        with open(TRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump(trades, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] {corrigidos} trades corrigidos e salvos!")
    else:
        print("[OK] Nenhum trade precisa ser corrigido")

if __name__ == '__main__':
    print("Corrigindo valores em trades_history.json...")
    print("=" * 50)
    corrigir_trades()
    print("=" * 50)
    print("[OK] Concluido! Recarregue a interface web para ver as mudancas.")

