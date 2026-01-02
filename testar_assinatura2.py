"""Teste: Como assinar VersionedTransaction - método correto"""
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
import base64

# Criar keypair de teste
keypair = Keypair()

print("="*70)
print("TESTE: Assinatura de VersionedTransaction - Método Correto")
print("="*70)
print()

# Criar uma transação dummy válida (pequena)
print("Criando transação dummy...")
try:
    # Uma transação versionada válida tem um formato específico
    # Vamos ver o que acontece quando tentamos criar
    dummy_bytes = b'\x80' + b'\x00' * 100  # Tenta criar algo
    
    try:
        tx = VersionedTransaction.from_bytes(dummy_bytes)
        print(f"  ✅ Transação criada: {type(tx)}")
        print(f"  Tipo de signatures: {type(tx.signatures)}")
        print(f"  signatures é lista?: {hasattr(tx.signatures, 'append')}")
        
        # Tentar assinar
        print()
        print("Tentando assinar...")
        try:
            # Método 1: sign() (se existir)
            if hasattr(tx, 'sign'):
                print("  Tentando tx.sign([keypair])...")
                tx.sign([keypair])
                print("  ✅ tx.sign() funcionou!")
            else:
                print("  ❌ tx.sign() não existe")
                
                # Método 2: sign_message + append
                print("  Tentando keypair.sign_message() + signatures.append()...")
                signature = keypair.sign_message(bytes(tx.message))
                print(f"  ✅ Assinatura criada: {type(signature)}")
                
                # Tentar adicionar à lista de assinaturas
                if hasattr(tx.signatures, 'append'):
                    tx.signatures.append(signature)
                    print("  ✅ Assinatura adicionada via append!")
                elif hasattr(tx.signatures, '__setitem__'):
                    tx.signatures[0] = signature
                    print("  ✅ Assinatura adicionada via index!")
                else:
                    print(f"  ❌ Não conseguiu adicionar assinatura. Tipo: {type(tx.signatures)}")
                    
        except Exception as e:
            print(f"  ❌ Erro ao assinar: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"  ❌ Erro ao criar transação: {type(e).__name__}: {e}")
        print("  (Esperado - transação dummy não é válida)")
        
except Exception as e:
    print(f"Erro geral: {e}")

print()
print("="*70)
print("Verificando se existe método de extensão do Rust...")
print("="*70)

# Verificar se há métodos mágicos
tx_dummy = None
try:
    dummy_bytes = b'\x80' + b'\x00' * 200
    tx_dummy = VersionedTransaction.from_bytes(dummy_bytes)
except:
    pass

if tx_dummy:
    # Verificar métodos especiais
    print(f"  __dict__: {hasattr(tx_dummy, '__dict__')}")
    if hasattr(tx_dummy, '__class__'):
        print(f"  __class__: {tx_dummy.__class__}")
    print(f"  dir() completo: {len([m for m in dir(tx_dummy)])} itens")











