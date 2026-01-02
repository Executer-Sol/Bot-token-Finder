#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa a mensagem específica do kora"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from message_parser import parse_token_message

mensagem_kora = """#kora ● $0.0₂25 258K FDV atualmente

Score: 16 (Spent: 5pts | Wallets: 4pts | Old: 2pts | Buys: 5pts)

2 wallets com 3k-5k em compras nos últimos minutos.

Detectado há 8 horas pela primeira vez nos 99K FDV.

CA: 8neDcPFwrvRNM9WXHCtHwTcKZrVm6wr4cs4PSN9Hpump"""

print("=" * 70)
print("🧪 TESTE: Mensagem do KORA")
print("=" * 70)
print()
print("📨 Mensagem:")
print("-" * 70)
print(mensagem_kora)
print("-" * 70)
print()

token_info = parse_token_message(mensagem_kora)

if token_info:
    print("✅ PARSE OK!")
    print(f"   Símbolo: {token_info.symbol}")
    print(f"   Score: {token_info.score}")
    print(f"   Preço: ${token_info.price}")
    print(f"   CA: {token_info.contract_address}")
    print(f"   Tempo: {token_info.minutes_detected} minutos" if token_info.minutes_detected else "   Tempo: Não detectado")
else:
    print("❌ PARSE FALHOU!")
    print()
    print("   Verificando elementos:")
    print(f"   - #SYMBOL: {'✅' if '#' in mensagem_kora else '❌'}")
    print(f"   - Score:: {'✅' if 'Score:' in mensagem_kora else '❌'}")
    print(f"   - CA:: {'✅' if 'CA:' in mensagem_kora else '❌'}")
    print(f"   - Preço ($): {'✅' if '$' in mensagem_kora else '❌'}")
    print()
    
    # Verifica regex de preço
    import re
    price_match = re.search(r'\$(\d+\.?\d*[₀₁₂₃₄₅₆₇₈₉]?\d*)', mensagem_kora)
    if price_match:
        print(f"   - Regex de preço encontrou: {price_match.group(1)}")
    else:
        print("   - Regex de preço NÃO encontrou nada")
    
    # Verifica regex de CA
    ca_match = re.search(r'CA:\s*`?([A-Za-z0-9]+)`?', mensagem_kora)
    if ca_match:
        print(f"   - Regex de CA encontrou: {ca_match.group(1)}")
    else:
        print("   - Regex de CA NÃO encontrou nada")

print()
print("=" * 70)










