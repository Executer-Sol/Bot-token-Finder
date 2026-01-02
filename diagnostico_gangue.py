"""
Script de diagnóstico para verificar por que o bot não identificou um token
"""
import asyncio
import sys
import io

# Garante encoding UTF-8 para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from gangue_client import GangueClient
import config
from bot_control import get_bot_state
from token_blacklist import get_blacklist_cache, is_blacklisted
from wallet_balance import get_wallet_balance

async def diagnosticar():
    """Diagnostica problemas na detecção de tokens"""
    print("="*70)
    print("🔍 DIAGNÓSTICO: Por que o bot não identificou o token?")
    print("="*70)
    
    # 1. Verifica se está usando Gangue
    print("\n1️⃣ Verificando configuração...")
    if not config.USE_GANGUE:
        print("   ❌ USE_GANGUE está desativado!")
        print("   💡 Configure USE_GANGUE=true no .env")
    else:
        print("   ✅ USE_GANGUE está ativado")
    
    # 2. Verifica cookies
    print("\n2️⃣ Verificando cookies...")
    gangue = GangueClient()
    cookies = gangue._get_cookies()
    if not cookies.get('session'):
        print("   ❌ Cookie 'session' não encontrado!")
        print("   💡 Configure cookies.json ou GANGUE_SESSION_COOKIE")
    else:
        print("   ✅ Cookie 'session' encontrado")
    
    # 3. Testa busca de tokens
    print("\n3️⃣ Testando busca de tokens da Gangue...")
    try:
        tokens = await gangue.get_latest_tokens(limit=20)
        print(f"   ✅ Encontrados {len(tokens)} tokens")
        
        if len(tokens) == 0:
            print("   ⚠️  Nenhum token encontrado!")
            print("   💡 Possíveis causas:")
            print("      - Site mudou estrutura")
            print("      - Cookies inválidos/expirados")
            print("      - Problema de conexão")
        else:
            print("\n   📋 Tokens encontrados:")
            for i, token in enumerate(tokens[:10], 1):
                print(f"      {i}. {token.symbol} - Score: {token.score} - CA: {token.contract_address[:20]}...")
            
            # Verifica se tem token com score 15
            tokens_score_15 = [t for t in tokens if t.score == 15]
            if tokens_score_15:
                print(f"\n   ✅ Encontrados {len(tokens_score_15)} token(s) com score 15:")
                for token in tokens_score_15:
                    print(f"      - {token.symbol} (CA: {token.contract_address})")
            else:
                print("\n   ⚠️  Nenhum token com score 15 encontrado na busca atual")
    except Exception as e:
        print(f"   ❌ Erro ao buscar tokens: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Verifica estado do bot
    print("\n4️⃣ Verificando estado do bot...")
    bot_state = get_bot_state()
    if not bot_state:
        print("   ❌ Bot está DESATIVADO!")
        print("   💡 Ative o bot na interface web")
    else:
        print("   ✅ Bot está ATIVO")
    
    # 5. Verifica score mínimo
    print("\n5️⃣ Verificando configurações de score...")
    print(f"   MIN_SCORE: {config.MIN_SCORE}")
    print(f"   MAX_SCORE: {config.MAX_SCORE}")
    if config.MIN_SCORE > 15:
        print(f"   ⚠️  MIN_SCORE ({config.MIN_SCORE}) > 15 - tokens com score 15 serão ignorados!")
    else:
        print("   ✅ Score 15 está dentro do range")
    
    # 6. Verifica saldo
    print("\n6️⃣ Verificando saldo da carteira...")
    try:
        balance = await get_wallet_balance()
        amount_needed = config.get_amount_by_score(15) + 0.01
        print(f"   Saldo atual: {balance['sol']:.4f} SOL")
        print(f"   Necessário para score 15: {amount_needed:.4f} SOL")
        if balance['sol'] < amount_needed:
            print(f"   ❌ Saldo insuficiente!")
        else:
            print("   ✅ Saldo suficiente")
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar saldo: {e}")
    
    # 7. Verifica blacklist
    print("\n7️⃣ Verificando blacklist...")
    get_blacklist_cache()
    # Não podemos verificar tokens específicos sem saber o CA, mas verificamos se há blacklist
    print("   ✅ Sistema de blacklist carregado")
    
    # 8. Verifica intervalo de polling
    print("\n8️⃣ Verificando intervalo de polling...")
    print(f"   GANGUE_POLL_INTERVAL: {config.GANGUE_POLL_INTERVAL} segundos")
    if config.GANGUE_POLL_INTERVAL > 10:
        print(f"   ⚠️  Intervalo muito alto ({config.GANGUE_POLL_INTERVAL}s) - pode perder tokens rápidos!")
    else:
        print("   ✅ Intervalo adequado")
    
    # 9. Verifica janela de tempo
    print("\n9️⃣ Verificando janela de tempo...")
    max_time = config.get_max_time_by_score(15)
    print(f"   Tempo máximo para score 15: {max_time} minutos")
    if max_time < 3:
        print(f"   ⚠️  Janela muito curta ({max_time}min) - pode perder tokens!")
    else:
        print("   ✅ Janela adequada")
    
    print("\n" + "="*70)
    print("✅ Diagnóstico completo!")
    print("="*70)
    
    await gangue.close()

if __name__ == '__main__':
    asyncio.run(diagnosticar())

