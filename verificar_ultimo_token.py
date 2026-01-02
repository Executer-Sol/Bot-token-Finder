"""
Verifica o último token que o bot viu e se comprou ou não
"""
import sys
import io
import os
import json
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verificar():
    print("="*70)
    print("🔍 VERIFICAÇÃO: Último Token Detectado")
    print("="*70)
    print()
    
    # Verifica se o bot viu algum token
    if not os.path.exists('last_token_detected.json'):
        print("❌ Bot ainda NÃO VIU nenhum token")
        print()
        print("Possíveis motivos:")
        print("  1. Bot não está rodando")
        print("  2. Bot não está conectado ao Telegram")
        print("  3. Nenhuma mensagem foi recebida ainda")
        print("  4. Canal do Telegram não configurado corretamente")
        print()
        return
    
    # Carrega último token
    with open('last_token_detected.json', 'r', encoding='utf-8') as f:
        token = json.load(f)
    
    print("✅ Bot VIU um token!")
    print()
    print("Último token detectado:")
    print("-"*70)
    print(f"  Símbolo: {token.get('symbol', 'N/A')}")
    print(f"  Score: {token.get('score', 'N/A')}")
    print(f"  Preço: ${token.get('price', 'N/A')}")
    print(f"  CA: {token.get('contract_address', 'N/A')}")
    minutes = token.get('minutes_detected')
    if minutes is not None:
        print(f"  Tempo desde detecção: {minutes} minutos")
    else:
        print(f"  Tempo: Não informado")
    detected_at = token.get('detected_at', '')
    if detected_at:
        try:
            dt = datetime.fromisoformat(detected_at)
            print(f"  Detectado em: {dt.strftime('%d/%m/%Y %H:%M:%S')}")
        except:
            print(f"  Detectado em: {detected_at}")
    print()
    
    # Verifica se comprou
    comprado = False
    if os.path.exists('trades_history.json'):
        with open('trades_history.json', 'r', encoding='utf-8') as f:
            trades = json.load(f)
        
        ca = token.get('contract_address')
        
        # Verifica em tokens ativos
        for trade in trades.get('active', []):
            if trade.get('contract_address') == ca:
                comprado = True
                print("="*70)
                print("✅ STATUS: COMPROU este token!")
                print("="*70)
                print(f"  TX: {trade.get('tx_signature', 'N/A')}")
                print(f"  Entrada: ${trade.get('entry_price', 'N/A')}")
                print(f"  Valor investido: {trade.get('amount_sol', 'N/A')} SOL")
                print()
                return
        
        # Verifica em tokens vendidos
        for trade in trades.get('sold', []):
            if trade.get('contract_address') == ca:
                comprado = True
                print("="*70)
                print("✅ STATUS: COMPROU e JÁ VENDEU este token!")
                print("="*70)
                print(f"  TX Compra: {trade.get('tx_signature', 'N/A')}")
                print(f"  Entrada: ${trade.get('entry_price', 'N/A')}")
                print(f"  Saída: ${trade.get('exit_price', 'N/A')}")
                print()
                return
    
    if not comprado:
        print("="*70)
        print("❌ STATUS: VIU mas NÃO COMPROU")
        print("="*70)
        print()
        print("Possíveis motivos:")
        print()
        
        # Verifica estado do bot
        if os.path.exists('bot_state.json'):
            with open('bot_state.json', 'r', encoding='utf-8') as f:
                state = json.load(f)
            if not state.get('enabled', True):
                print("  ❌ Bot estava DESATIVADO")
            else:
                print("  ✅ Bot estava ATIVADO")
        
        # Verifica score
        score = token.get('score', 0)
        if score < 15:
            print(f"  ❌ Score {score} abaixo do mínimo (15)")
        elif score > 21:
            print(f"  ❌ Score {score} acima do máximo (21)")
        else:
            print(f"  ✅ Score {score} dentro do range")
        
        # Verifica tempo
        minutes = token.get('minutes_detected')
        if minutes is not None:
            if score <= 17:
                max_time = 3
            elif score <= 19:
                max_time = 5
            else:
                max_time = 1
            
            if minutes > max_time:
                print(f"  ❌ Detectado há {minutes} minutos (máx: {max_time}min)")
            else:
                print(f"  ✅ Dentro da janela de tempo ({minutes}min <= {max_time}min)")
        
        print()
        print("💡 Use 'python diagnosticar_token.py' para diagnóstico completo")
        print()
    
    print("="*70)

if __name__ == "__main__":
    verificar()











