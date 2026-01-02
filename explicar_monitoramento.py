"""
Explicação: Como o bot monitora preço e calcula % de alta
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print("COMO O BOT MONITORA O PRECO E CALCULA % QUE SUBIU")
print("="*70)

print("\n1. DEPOIS DE COMPRAR O TOKEN:")
print("   - Bot salva o preco de ENTRADA (ex: $0.000062)")
print("   - Inicia um loop que roda a cada 10 segundos")
print("   - Esse loop fica rodando em background")

print("\n2. A CADA 10 SEGUNDOS, O BOT FAZ:")
print("   a) Busca preco ATUAL do token na DexScreener API")
print("      URL: https://api.dexscreener.com/latest/dex/tokens/{CA}")
print("   b) Compara preco atual com preco de entrada")
print("   c) Calcula o MULTIPLO e % de alta")

print("\n3. EXEMPLO DE CALCULO:")
print("   Preco de ENTRADA: $0.000062")
print("   Preco ATUAL:      $0.000124")
print("   ")
print("   Multiplo = Preco Atual / Preco Entrada")
print("   Multiplo = 0.000124 / 0.000062")
print("   Multiplo = 2.0x")
print("   ")
print("   % Alta = (Multiplo - 1) x 100")
print("   % Alta = (2.0 - 1) x 100")
print("   % Alta = 100% de alta")

print("\n4. QUANDO ATINGE TAKE PROFIT:")
print("   Se multiplo >= 2.0x (Score 15-17):")
print("   - Vende 50% do token")
print("   - Continua monitorando o resto")
print("   ")
print("   Se multiplo >= 4.0x:")
print("   - Vende mais 20%")
print("   ")
print("   E assim por diante...")

print("\n5. ONDE ISSO ACONTECE NO CODIGO:")
print("   Arquivo: take_profit.py")
print("   - Funcao: check_price_and_sell()")
print("   - Usa: price_monitor.py para buscar preco")
print("   - Loop: roda a cada 10 segundos (linha 112)")

print("\n6. EXEMPLO DE LOG EM TEMPO REAL:")
print("   Token comprado: SHIRLEY @ $0.000082")
print("   ")
print("   [T+10s] Preco: $0.000082 = 1.0x (0% alta)")
print("   [T+20s] Preco: $0.000095 = 1.16x (16% alta)")
print("   [T+30s] Preco: $0.000110 = 1.34x (34% alta)")
print("   [T+40s] Preco: $0.000164 = 2.0x (100% alta) <- ATINGIU TP!")
print("   [ACAO] Vende 50% do token automaticamente")
print("   [T+50s] Preco: $0.000200 = 2.44x (continua monitorando...)")
print("   [T+60s] Preco: $0.000328 = 4.0x (200% alta) <- ATINGIU TP 2!")
print("   [ACAO] Vende mais 20%")

print("\n" + "="*70)
print("RESUMO:")
print("="*70)
print("✅ Bot usa DexScreener API para preco atual")
print("✅ Compara com preco de entrada salvo")
print("✅ Calcula multiplo e % automaticamente")
print("✅ Vende quando atinge take profits configurados")
print("✅ Roda a cada 10 segundos em background")
print("="*70)

