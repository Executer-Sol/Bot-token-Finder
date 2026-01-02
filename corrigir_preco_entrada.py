"""
Script para corrigir preços de entrada inválidos nos trades
Usa o preço inicial do token detectado como referência
"""
import json
import os
from detected_tokens_tracker import get_all_detected_tokens

TRADES_FILE = 'trades_history.json'
DETECTED_TOKENS_FILE = 'detected_tokens.json'

def corrigir_precos_entrada():
    """Corrige preços de entrada inválidos usando preço inicial detectado"""
    
    # Carrega trades
    if not os.path.exists(TRADES_FILE):
        print("ERRO: Arquivo trades_history.json nao encontrado")
        return
    
    with open(TRADES_FILE, 'r', encoding='utf-8') as f:
        trades_data = json.load(f)
    
    # Carrega tokens detectados
    detected_tokens = get_all_detected_tokens(limit=1000)
    
    # Cria mapa de CA -> preço inicial
    price_map = {}
    for token in detected_tokens:
        ca = token.get('contract_address')
        initial_price = token.get('initial_price', 0)
        if ca and initial_price > 1e-8:  # Preço válido
            price_map[ca] = initial_price
    
    corrigidos = 0
    
    # Corrige trades ativos
    for trade in trades_data.get('active', []):
        ca = trade.get('contract_address')
        entry_price = trade.get('entry_price', 0)
        
        # Se preço de entrada é inválido (< 1e-8)
        if entry_price < 1e-8 and ca in price_map:
            preco_correto = price_map[ca]
            print(f"Corrigindo {trade.get('symbol', 'N/A')} ({ca[:8]}...):")
            print(f"   Preco antigo: {entry_price:.10f}")
            print(f"   Preco novo: {preco_correto:.10f}")
            
            trade['entry_price'] = preco_correto
            trade['current_price'] = preco_correto  # Atualiza também o preço atual
            trade['multiple'] = 1.0
            trade['percent_change'] = 0.0
            
            corrigidos += 1
    
    # Corrige trades vendidos
    for trade in trades_data.get('sold', []):
        ca = trade.get('contract_address')
        entry_price = trade.get('entry_price', 0)
        
        if entry_price < 1e-8 and ca in price_map:
            preco_correto = price_map[ca]
            print(f"Corrigindo {trade.get('symbol', 'N/A')} VENDIDO ({ca[:8]}...):")
            print(f"   Preco antigo: {entry_price:.10f}")
            print(f"   Preco novo: {preco_correto:.10f}")
            
            trade['entry_price'] = preco_correto
            
            # Recalcula lucro/perda se tiver final_price
            if trade.get('final_price', 0) > 0:
                final_price = trade['final_price']
                final_multiple = final_price / preco_correto if preco_correto > 0 else 1.0
                trade['profit_loss_percent'] = ((final_multiple - 1) * 100)
                
                # Recalcula profit_loss_sol
                amount_sol = trade.get('amount_sol', trade.get('amount_usdc', 0) / 100.0)
                total_sold_percent = trade.get('total_sold_percent', 100.0)
                entry_value_sol = amount_sol
                final_value_sol = entry_value_sol * final_multiple * (total_sold_percent / 100)
                profit_loss_sol = final_value_sol - (entry_value_sol * (total_sold_percent / 100))
                
                trade['profit_loss_sol'] = profit_loss_sol
                trade['final_value_sol'] = final_value_sol
            
            corrigidos += 1
    
    if corrigidos > 0:
        # Salva backup
        backup_file = f'trades_history_backup_antes_correcao_{os.path.basename(TRADES_FILE)}'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(trades_data, f, indent=2, ensure_ascii=False)
        print(f"\nBackup criado: {backup_file}")
        
        # Salva corrigido
        with open(TRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump(trades_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{corrigidos} trade(s) corrigido(s)!")
    else:
        print("Nenhum trade precisa de correcao")

if __name__ == '__main__':
    print("Corrigindo precos de entrada invalidos...\n")
    corrigir_precos_entrada()

