"""Teste: Como assinar VersionedTransaction corretamente"""
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
import base64

# Criar keypair de teste
keypair = Keypair()

print("="*70)
print("TESTE: Assinatura de VersionedTransaction")
print("="*70)
print()

# Verificar métodos disponíveis
print("Métodos de VersionedTransaction:")
methods = [m for m in dir(VersionedTransaction) if not m.startswith('_')]
print(f"  Total: {len(methods)} métodos")
print(f"  Métodos com 'sign': {[m for m in methods if 'sign' in m.lower()]}")
print(f"  Métodos com 'add': {[m for m in methods if 'add' in m.lower()]}")
print()

# Testar se sign existe como método de classe
print("Testando VersionedTransaction.sign:")
print(f"  hasattr(VersionedTransaction, 'sign'): {hasattr(VersionedTransaction, 'sign')}")
print(f"  hasattr(VersionedTransaction, 'add_signature'): {hasattr(VersionedTransaction, 'add_signature')}")
print()

# Testar método de instância
print("Criando transação dummy para testar métodos de instância...")
try:
    # Criar uma transação dummy (vai dar erro, mas só queremos ver os métodos)
    dummy_bytes = b'\x00' * 100
    try:
        tx = VersionedTransaction.from_bytes(dummy_bytes)
        print(f"  Instância criada: {type(tx)}")
        print(f"  hasattr(tx, 'sign'): {hasattr(tx, 'sign')}")
        print(f"  hasattr(tx, 'add_signature'): {hasattr(tx, 'add_signature')}")
        if hasattr(tx, 'sign'):
            print(f"  type(tx.sign): {type(tx.sign)}")
            import inspect
            sig = inspect.signature(tx.sign)
            print(f"  tx.sign signature: {sig}")
    except Exception as e:
        print(f"  Erro ao criar instância (esperado): {type(e).__name__}")
except Exception as e:
    print(f"Erro: {e}")

print()
print("="*70)











