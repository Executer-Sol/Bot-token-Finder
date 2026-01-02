"""
Script para verificar se o stop loss está funcionando
"""
import json
import os
import sys
import io
from datetime import datetime, timezone

# Configura encoding para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verificar_posicoes():
    """Verifica posições ativas e calcula tempo desde compra"""
    print("="*70)
    print("🔍 VERIFICAÇÃO: Stop Loss por Tempo")
    print("="*70)
    print()
    
    # Verifica trades ativos
    if not os.path.exists('trades_history.json'):
        print("❌ Arquivo trades_history.json não encontrado")
        return
    
    with open('trades_history.json', 'r', encoding='utf-8') as f:
        trades = json.load(f)
    
    active = trades.get('active', [])
    
    if len(active) == 0:
        print("✅ Nenhum token ativo no momento")
        return
    
    print(f"📊 Tokens Ativos: {len(active)}")
    print()
    
    # Importa config
    try:
        import config
        stop_loss_time = config.STOP_LOSS_TIME_MINUTES
        stop_loss_multiple = config.STOP_LOSS_MIN_MULTIPLE
    except:
        stop_loss_time = 5
        stop_loss_multiple = 1.0
    
    print(f"⚙️  Configuração:")
    print(f"   STOP_LOSS_TIME_MINUTES: {stop_loss_time}")
    print(f"   STOP_LOSS_MIN_MULTIPLE: {stop_loss_multiple}")
    print()
    
    now = datetime.now(timezone.utc)
    
    for trade in active:
        symbol = trade.get('symbol', 'N/A')
        ca = trade.get('contract_address', 'N/A')
        timestamp = trade.get('timestamp', '')
        multiple = trade.get('multiple', 1.0)
        
        try:
            # Parse timestamp
            if 'T' in timestamp:
                if timestamp.endswith('Z'):
                    bought_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    bought_at = datetime.fromisoformat(timestamp)
                    if bought_at.tzinfo is None:
                        bought_at = bought_at.replace(tzinfo=timezone.utc)
            else:
                bought_at = datetime.fromisoformat(timestamp)
                if bought_at.tzinfo is None:
                    bought_at = bought_at.replace(tzinfo=timezone.utc)
            
            time_since_buy = (now - bought_at).total_seconds() / 60  # minutos
            
            print(f"📌 {symbol} ({ca[:8]}...)")
            print(f"   Comprado há: {time_since_buy:.1f} minutos")
            print(f"   Múltiplo atual: {multiple:.3f}x")
            print(f"   Status: ", end='')
            
            if time_since_buy >= stop_loss_time:
                # Verifica condições
                max_reached = trade.get('max_multiple_reached', multiple)
                never_moved = max_reached < 1.1
                below_minimum = multiple < stop_loss_multiple
                
                if never_moved or below_minimum:
                    print(f"⚠️  DEVERIA TER VENDIDO!")
                    print(f"      Tempo: {time_since_buy:.1f} min >= {stop_loss_time} min")
                    print(f"      Condição: {'Nunca subiu acima de 1.1x' if never_moved else f'Caiu abaixo de {stop_loss_multiple}x'}")
                    print(f"      Máximo atingido: {max_reached:.3f}x")
                else:
                    print(f"✅ Ainda dentro dos parâmetros")
                    print(f"      Máximo atingido: {max_reached:.3f}x (>= 1.1x)")
            else:
                print(f"⏳ Aguardando {stop_loss_time} minutos")
                print(f"      Faltam: {stop_loss_time - time_since_buy:.1f} minutos")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")
            print()
    
    print("="*70)
    print("💡 Dica: Verifique os logs do bot para ver se há erros no take_profit.py")
    print("="*70)

if __name__ == '__main__':
    verificar_posicoes()

