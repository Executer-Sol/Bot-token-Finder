"""
Script para corrigir time_to_sell nos trades vendidos manualmente
Recalcula baseado nos timestamps reais de compra e venda
"""
import json
import sys
import io
from datetime import datetime, timezone

# Garante encoding UTF-8 para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TRADES_FILE = 'trades_history.json'

def corrigir_time_to_sell():
    """Corrige time_to_sell para todos os trades vendidos manualmente"""
    try:
        # Carrega trades
        with open(TRADES_FILE, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        
        corrigidos = 0
        
        for trade in trades.get('sold', []):
            if trade.get('sell_reason') == 'manual':
                timestamp_str = trade.get('timestamp', '')
                sold_at_str = trade.get('sold_at', '')
                
                if timestamp_str and sold_at_str:
                    try:
                        # Parse timestamp da compra
                        if 'T' in timestamp_str:
                            if timestamp_str.endswith('Z'):
                                bought_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            elif '+' in timestamp_str or timestamp_str.count('-') > 2:
                                bought_at = datetime.fromisoformat(timestamp_str)
                            else:
                                bought_at = datetime.fromisoformat(timestamp_str)
                                if bought_at.tzinfo is None:
                                    bought_at = bought_at.replace(tzinfo=timezone.utc)
                        else:
                            bought_at = datetime.fromisoformat(timestamp_str)
                            if bought_at.tzinfo is None:
                                bought_at = bought_at.replace(tzinfo=timezone.utc)
                        
                        # Parse sold_at
                        if 'T' in sold_at_str:
                            if sold_at_str.endswith('Z'):
                                sold_at = datetime.fromisoformat(sold_at_str.replace('Z', '+00:00'))
                            elif '+' in sold_at_str or sold_at_str.count('-') > 2:
                                sold_at = datetime.fromisoformat(sold_at_str)
                            else:
                                sold_at = datetime.fromisoformat(sold_at_str)
                                if sold_at.tzinfo is None:
                                    sold_at = sold_at.replace(tzinfo=timezone.utc)
                        else:
                            sold_at = datetime.fromisoformat(sold_at_str)
                            if sold_at.tzinfo is None:
                                sold_at = sold_at.replace(tzinfo=timezone.utc)
                        
                        # Calcula time_to_sell correto
                        time_to_sell = (sold_at - bought_at).total_seconds() / 60  # minutos
                        
                        # Atualiza apenas se for diferente
                        if abs(trade.get('time_to_sell', 0) - time_to_sell) > 0.1:
                            old_value = trade.get('time_to_sell', 0)
                            trade['time_to_sell'] = round(time_to_sell, 2)
                            print(f"✅ {trade.get('symbol', 'N/A')}: {old_value:.2f} min → {time_to_sell:.2f} min")
                            corrigidos += 1
                        else:
                            print(f"✓ {trade.get('symbol', 'N/A')}: já está correto ({time_to_sell:.2f} min)")
                    except Exception as e:
                        print(f"❌ Erro ao corrigir {trade.get('symbol', 'N/A')}: {e}")
        
        if corrigidos > 0:
            # Salva correções
            with open(TRADES_FILE, 'w', encoding='utf-8') as f:
                json.dump(trades, f, indent=2, ensure_ascii=False)
            print(f"\n✅ {corrigidos} trade(s) corrigido(s)!")
        else:
            print("\n✓ Nenhuma correção necessária.")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    corrigir_time_to_sell()

