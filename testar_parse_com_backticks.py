"""
Teste: Parse com CA entre backticks
"""
import sys
import io
from message_parser import parse_token_message

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Mensagem com CA entre backticks (formato real do Telegram)
mensagem_com_backticks = """#OCR ● $0.0₃67 67K FDV atualmente

Score: 17 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 5pts)

2 wallets com 1k-3k em compras nos últimos minutos.

Detectado há 27 minutos pela primeira vez nos 7.0K FDV.

CA: `4JZrxzQqubXq8fu3JenGZ48av9o9KxaXgrXHfwmYpump`"""

print("="*70)
print("TESTE: Parse com CA entre backticks")
print("="*70)
print()
print("Mensagem:")
print(mensagem_com_backticks)
print()
print("-"*70)
print()

token_info = parse_token_message(mensagem_com_backticks)

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
    print("O regex precisa aceitar backticks ao redor da CA")











