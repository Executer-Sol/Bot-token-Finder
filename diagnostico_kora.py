#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnóstico para verificar por que o token 'kora' não foi identificado"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from gangue_client import GangueClient
import config
from bot_control import get_bot_state

async def main():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO: Por que 'kora' não foi identificado?")
    print("=" * 60)
    print()
    
    # 1. Verifica configuração
    print("1️⃣  CONFIGURAÇÃO:")
    print(f"   USE_GANGUE: {getattr(config, 'USE_GANGUE', 'NÃO DEFINIDO')}")
    print(f"   MIN_SCORE: {config.MIN_SCORE}")
    print(f"   MAX_SCORE: {config.MAX_SCORE}")
    print(f"   Bot ativo: {get_bot_state()}")
    print()
    
    # 2. Testa busca de tokens
    print("2️⃣  BUSCANDO TOKENS DA GANGUE...")
    gangue = GangueClient(
        session_cookie=config.GANGUE_SESSION_COOKIE if hasattr(config, 'GANGUE_SESSION_COOKIE') else None,
        ga_cookie=config.GANGUE_GA_COOKIE if hasattr(config, 'GANGUE_GA_COOKIE') else None,
        cookies_file=getattr(config, 'GANGUE_COOKIES_FILE', 'cookies.json')
    )
    
    try:
        tokens = await gangue.get_latest_tokens(limit=20)
        print(f"   ✅ Encontrados {len(tokens)} tokens")
        print()
        
        # 3. Procura por 'kora'
        print("3️⃣  PROCURANDO POR 'KORA'...")
        kora_found = False
        for token in tokens:
            if token.symbol.upper() == 'KORA' or 'kora' in token.symbol.lower():
                kora_found = True
                print(f"   ✅ KORA ENCONTRADO!")
                print(f"      Símbolo: {token.symbol}")
                print(f"      Score: {token.score}")
                print(f"      CA: {token.contract_address}")
                print(f"      Preço: ${token.price}")
                print(f"      Minutos detectado: {token.minutes_detected}")
                print()
                
                # Verifica se passaria nas validações
                print("4️⃣  VALIDAÇÕES DO BOT:")
                
                # Score mínimo
                if token.score < config.MIN_SCORE:
                    print(f"   ❌ Score {token.score} < MIN_SCORE {config.MIN_SCORE}")
                else:
                    print(f"   ✅ Score {token.score} >= MIN_SCORE {config.MIN_SCORE}")
                
                # Score máximo
                if token.score > config.MAX_SCORE:
                    print(f"   ❌ Score {token.score} > MAX_SCORE {config.MAX_SCORE}")
                else:
                    print(f"   ✅ Score {token.score} <= MAX_SCORE {config.MAX_SCORE}")
                
                # Valor configurado
                amount_sol = config.get_amount_by_score(token.score)
                if amount_sol == 0:
                    print(f"   ❌ Score {token.score} não tem valor configurado (amount_sol = 0)")
                else:
                    print(f"   ✅ Valor configurado: {amount_sol} SOL")
                
                # Janela de tempo
                max_time = config.get_max_time_by_score(token.score)
                if token.minutes_detected is None:
                    token.minutes_detected = 0
                if token.minutes_detected > max_time:
                    print(f"   ❌ Detectado há {token.minutes_detected} minutos > máximo {max_time} minutos")
                else:
                    print(f"   ✅ Detectado há {token.minutes_detected} minutos <= máximo {max_time} minutos")
                
                print()
                break
        
        if not kora_found:
            print("   ❌ KORA NÃO ENCONTRADO na lista de tokens!")
            print()
            print("   📋 Tokens encontrados:")
            for i, token in enumerate(tokens[:10], 1):
                print(f"      {i}. {token.symbol} (Score: {token.score}, CA: {token.contract_address[:20]}...)")
            print()
            print("   💡 Possíveis causas:")
            print("      - Token não está mais na lista (já foi removido)")
            print("      - Parsing do HTML falhou")
            print("      - Site mudou estrutura")
            print("      - Cookies inválidos/expirados")
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar tokens: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await gangue.close()
    
    print()
    print("=" * 60)
    print("✅ Diagnóstico concluído!")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())










