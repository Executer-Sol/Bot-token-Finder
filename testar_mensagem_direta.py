#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa parse de mensagem específica do Telegram"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from message_parser import parse_token_message

# Mensagens de exemplo baseadas na imagem
mensagens_teste = [
    """#kora ● $0.0225 258K FDV atualmente

Score: 16 (Spent: 5pts | Wallets: 4pts | Old: 2pts | Buys: 5pts)

2 wallets com 3k-5k em compras nos últimos minutos.

Detectado há 8 horas pela primeira vez nos 99K FDV.

CA: 8neDcPFwrvRNM9WXHCtHwTcKZrVm6wr4cs4PSN9Hpump""",
    
    """#GOOP ● $0.0336 37K FDV atualmente

Score: 15 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 3pts)

2 wallets com 1k-3k em compras nos últimos minutos.

Detectado há 2 minutos pela primeira vez nos 20K FDV.

CA: 54FE9JPbxgnv5hAEFXpb13M9wumR61eZemwJyvVHpump""",
    
    """#GOD ● $0.00607998 128K FDV atualmente

Score: 16 (Spent: 3pts | Wallets: 4pts | Old: 4pts | Buys: 5pts)

2 wallets com 1k-3k em compras nos últimos minutos.

Detectado há 18 minutos pela primeira vez nos 79K FDV.

CA: GQ6mUfsySbXgDRGjewog4XoRWpYNkJ7YtSEYuMjCbonk""",
]

print("=" * 70)
print("🧪 TESTE DE PARSE DE MENSAGENS")
print("=" * 70)
print()

for i, mensagem in enumerate(mensagens_teste, 1):
    print(f"📨 Mensagem {i}:")
    print("-" * 70)
    print(mensagem[:150] + "...")
    print()
    
    token_info = parse_token_message(mensagem)
    
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
        print(f"   - #SYMBOL: {'✅' if '#' in mensagem else '❌'}")
        print(f"   - Score:: {'✅' if 'Score:' in mensagem else '❌'}")
        print(f"   - CA:: {'✅' if 'CA:' in mensagem else '❌'}")
        print(f"   - Preço ($): {'✅' if '$' in mensagem else '❌'}")
    
    print()
    print("=" * 70)
    print()










