"""
Script para converter TODOS os trades para SOL
"""
import json
import os
import sys
import io

# Configura encoding para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TRADES_FILE = 'trades_history.json'

def converter_todos_para_sol():
    """Converte todos os campos USDC para SOL"""
    if not os.path.exists(TRADES_FILE):
        print(f"Arquivo {TRADES_FILE} nao encontrado")
        return
    
    with open(TRADES_FILE, 'r', encoding='utf-8') as f:
        trades = json.load(f)
    
    convertidos = 0
    
    # Converte trades ativos
    for trade in trades.get('active', []):
        mudou = False
        
        if 'amount_usdc' in trade and 'amount_sol' not in trade:
            trade['amount_sol'] = trade['amount_usdc'] / 100.0
            del trade['amount_usdc']
            mudou = True
        
        if mudou:
            print(f"[OK] Convertido {trade['symbol']}: amount_usdc -> amount_sol")
            convertidos += 1
    
    # Converte trades vendidos
    for trade in trades.get('sold', []):
        mudou = False
        
        if 'amount_usdc' in trade and 'amount_sol' not in trade:
            trade['amount_sol'] = trade['amount_usdc'] / 100.0
            del trade['amount_usdc']
            mudou = True
        
        if 'profit_loss_usdc' in trade and 'profit_loss_sol' not in trade:
            trade['profit_loss_sol'] = trade['profit_loss_usdc'] / 100.0
            del trade['profit_loss_usdc']
            mudou = True
        
        if 'final_value_usdc' in trade and 'final_value_sol' not in trade:
            trade['final_value_sol'] = trade['final_value_usdc'] / 100.0
            del trade['final_value_usdc']
            mudou = True
        
        if mudou:
            print(f"[OK] Convertido {trade['symbol']} (vendido)")
            convertidos += 1
    
    if convertidos > 0:
        with open(TRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump(trades, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] {convertidos} trades convertidos para SOL!")
    else:
        print("[OK] Nenhum trade precisa ser convertido")
    
    # Mostra resumo
    print(f"\nResumo:")
    print(f"  Tokens ativos: {len(trades.get('active', []))}")
    print(f"  Tokens vendidos: {len(trades.get('sold', []))}")

if __name__ == '__main__':
    print("Convertendo todos os trades para SOL...")
    print("=" * 50)
    converter_todos_para_sol()
    print("=" * 50)
    print("[OK] Concluido!")

