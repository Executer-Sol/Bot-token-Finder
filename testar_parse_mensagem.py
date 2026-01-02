"""
Teste rápido: Cole uma mensagem do Telegram aqui para ver se o parse funciona
"""
import sys
import io
from message_parser import parse_token_message

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Exemplo de mensagem (substitua pela mensagem real)
mensagem_exemplo = """#oddbit ● $0.0₃62 62K FDV atualmente

Score: 15 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 3pts)

2 wallets com 1k-3k em compras nos últimos minutos.

Detectado há 6 minutos pela primeira vez nos 20K FDV.

CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump"""

print("="*70)
print("TESTE DE PARSE DE MENSAGEM")
print("="*70)
print()

# Substitua pela mensagem real se quiser testar outra
mensagem = mensagem_exemplo

print("Mensagem:")
print(mensagem)
print()
print("-"*70)
print()

token_info = parse_token_message(mensagem)

if token_info:
    print("✅ PARSE FUNCIONOU!")
    print()
    print(f"Símbolo: {token_info.symbol}")
    print(f"Score: {token_info.score}")
    print(f"Preço: ${token_info.price}")
    print(f"CA: {token_info.contract_address}")
    print(f"FDV: {token_info.fdv}")
    if token_info.minutes_detected:
        print(f"Tempo: {token_info.minutes_detected} minutos")
    else:
        print("Tempo: Não detectado")
else:
    print("❌ PARSE FALHOU!")
    print()
    print("A mensagem não foi reconhecida.")
    print()
    print("Verifique se contém:")
    print("  - Símbolo com # (ex: #oddbit)")
    print("  - Preço com $ (ex: $0.000062)")
    print("  - Score (ex: Score: 15)")
    print("  - CA (ex: CA: A6RTAd...)")
    print()
    print("💡 Use: python diagnosticar_token.py para diagnóstico completo")











