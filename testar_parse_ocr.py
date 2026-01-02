"""
Teste específico: Por que o parse falha para #OCR?
"""
import sys
import io
from message_parser import parse_token_message

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Mensagem real que está chegando
mensagem_ocr = """#OCR ● $0.0₃67 67K FDV atualmente

Score: 17 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 5pts)

2 wallets com 1k-3k em compras nos últimos minutos.

Detectado há 27 minutos pela primeira vez nos 7.0K FDV.

CA: 4JZrxzQqubXq8fu3JenGZ48av9o9KxaXgrXHfwmYpump"""

print("="*70)
print("TESTE: Parse da mensagem #OCR")
print("="*70)
print()
print("Mensagem completa:")
print(mensagem_ocr)
print()
print("-"*70)
print()

token_info = parse_token_message(mensagem_ocr)

if token_info:
    print("✅ PARSE FUNCIONOU!")
    print()
    print(f"Símbolo: {token_info.symbol}")
    print(f"Score: {token_info.score}")
    print(f"Preço: ${token_info.price}")
    print(f"CA: {token_info.contract_address}")
    print(f"Tempo: {token_info.minutes_detected} minutos")
else:
    print("❌ PARSE FALHOU!")
    print()
    print("Vamos verificar cada elemento:")
    print()
    
    import re
    
    # Testa cada regex
    symbol_match = re.search(r'#(\w+)', mensagem_ocr)
    print(f"1. Símbolo (#OCR): {'✅' if symbol_match else '❌'}")
    if symbol_match:
        print(f"   Encontrado: {symbol_match.group(1)}")
    
    price_match = re.search(r'\$(\d+\.?\d*[₀₁₂₃₄₅₆₇₈₉]?\d*)', mensagem_ocr)
    print(f"2. Preço ($0.0₃67): {'✅' if price_match else '❌'}")
    if price_match:
        print(f"   Encontrado: {price_match.group(1)}")
    
    score_match = re.search(r'Score:\s*(\d+)', mensagem_ocr)
    print(f"3. Score (Score: 17): {'✅' if score_match else '❌'}")
    if score_match:
        print(f"   Encontrado: {score_match.group(1)}")
    
    ca_match = re.search(r'CA:\s*([A-Za-z0-9]+)', mensagem_ocr)
    print(f"4. CA (CA: 4JZrxzQ...): {'✅' if ca_match else '❌'}")
    if ca_match:
        print(f"   Encontrado: {ca_match.group(1)}")
    
    print()
    print("Se algum elemento falhou, esse é o problema!")











