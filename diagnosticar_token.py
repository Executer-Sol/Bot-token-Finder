"""
Diagnóstico: Por que o bot não comprou um token?
Cole a mensagem do Telegram aqui e veja o que acontece
"""
import sys
import io
from message_parser import parse_token_message
from bot_control import get_bot_state
from token_blacklist import is_blacklisted
from config import get_amount_by_score, get_max_time_by_score, MIN_SCORE, MAX_SCORE
from daily_loss_limit import check_daily_loss_limit
import config

# Configura encoding para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def diagnosticar_mensagem(mensagem_telegram: str):
    """Diagnostica por que um token não foi comprado"""
    print("="*70)
    print("🔍 DIAGNÓSTICO: Por que o token não foi comprado?")
    print("="*70)
    print()
    
    # 1. Parse da mensagem
    print("1️⃣ PARSE DA MENSAGEM")
    print("-"*70)
    token_info = parse_token_message(mensagem_telegram)
    
    if not token_info:
        print("❌ ERRO: Não conseguiu fazer parse da mensagem!")
        print()
        print("Mensagem recebida:")
        print(mensagem_telegram)
        print()
        print("💡 Verifique se a mensagem contém:")
        print("   - Símbolo (ex: #oddbit)")
        print("   - Preço (ex: $0.000062)")
        print("   - Score (ex: Score: 15)")
        print("   - CA (ex: CA: A6RTAd...)")
        return
    
    print("✅ Parse OK!")
    print(f"   Símbolo: {token_info.symbol}")
    print(f"   Score: {token_info.score}")
    print(f"   Preço: ${token_info.price}")
    print(f"   CA: {token_info.contract_address}")
    print(f"   Tempo: {token_info.minutes_detected} minutos" if token_info.minutes_detected else "   Tempo: Não detectado")
    print()
    
    # 2. Verifica estado do bot
    print("2️⃣ ESTADO DO BOT")
    print("-"*70)
    bot_enabled = get_bot_state()
    if not bot_enabled:
        print("❌ PROBLEMA: Bot está DESATIVADO!")
        print("   Solução: Ative o bot na interface web (http://localhost:5000)")
        print()
    else:
        print("✅ Bot está ATIVADO")
        print()
    
    # 3. Verifica blacklist
    print("3️⃣ BLACKLIST")
    print("-"*70)
    if is_blacklisted(token_info.contract_address):
        print(f"❌ PROBLEMA: Token está na BLACKLIST!")
        print(f"   CA: {token_info.contract_address}")
        print("   Solução: Remova da blacklist na interface web")
        print()
    else:
        print("✅ Token NÃO está na blacklist")
        print()
    
    # 4. Verifica score
    print("4️⃣ SCORE")
    print("-"*70)
    if token_info.score < MIN_SCORE:
        print(f"❌ PROBLEMA: Score {token_info.score} abaixo do mínimo ({MIN_SCORE})")
        print("   Solução: Configure MIN_SCORE menor ou ENABLE_LOW_SCORE=true")
        print()
    elif token_info.score > MAX_SCORE:
        print(f"❌ PROBLEMA: Score {token_info.score} acima do máximo ({MAX_SCORE})")
        print("   Solução: Configure MAX_SCORE maior")
        print()
    else:
        print(f"✅ Score {token_info.score} está dentro do range ({MIN_SCORE}-{MAX_SCORE})")
        print()
    
    # 5. Verifica valor configurado
    print("5️⃣ VALOR CONFIGURADO")
    print("-"*70)
    amount_sol = get_amount_by_score(token_info.score)
    if amount_sol == 0:
        print(f"❌ PROBLEMA: Score {token_info.score} não tem valor configurado!")
        print("   Solução: Configure AMOUNT_SOL_* no .env ou config.py")
        print()
    else:
        print(f"✅ Valor configurado: {amount_sol} SOL")
        print()
    
    # 6. Verifica janela de tempo
    print("6️⃣ JANELA DE TEMPO")
    print("-"*70)
    if token_info.minutes_detected is not None:
        max_time = get_max_time_by_score(token_info.score)
        if token_info.minutes_detected > max_time:
            print(f"❌ PROBLEMA: Token detectado há {token_info.minutes_detected} minutos")
            print(f"   Máximo permitido para score {token_info.score}: {max_time} minutos")
            print("   Solução: Bot só compra dentro da janela de tempo configurada")
            print()
        else:
            print(f"✅ Dentro da janela: {token_info.minutes_detected} minutos < {max_time} minutos máximo")
            print()
    else:
        print("⚠️  Tempo desde detecção não informado na mensagem")
        print("   Bot vai tentar comprar mesmo assim")
        print()
    
    # 7. Verifica limite diário
    print("7️⃣ LIMITE DE PERDA DIÁRIO")
    print("-"*70)
    max_daily_loss = getattr(config, 'MAX_DAILY_LOSS_SOL', None)
    if max_daily_loss:
        limit_reached, stats = check_daily_loss_limit(max_daily_loss)
        if limit_reached:
            print(f"❌ PROBLEMA: Limite de perda diário atingido!")
            print(f"   Perda total: {stats['total_loss']:.4f} SOL")
            print(f"   Limite: {max_daily_loss} SOL")
            print("   Solução: Configure MAX_DAILY_LOSS_SOL maior ou resete")
            print()
        else:
            print(f"✅ Limite diário OK ({stats['total_loss']:.4f} SOL perdido)")
            print()
    else:
        print("✅ Sem limite de perda configurado")
        print()
    
    # 8. Resumo
    print("="*70)
    print("📊 RESUMO")
    print("="*70)
    
    problemas = []
    if not bot_enabled:
        problemas.append("Bot desativado")
    if is_blacklisted(token_info.contract_address):
        problemas.append("Token na blacklist")
    if token_info.score < MIN_SCORE or token_info.score > MAX_SCORE:
        problemas.append(f"Score fora do range ({MIN_SCORE}-{MAX_SCORE})")
    if amount_sol == 0:
        problemas.append("Score sem valor configurado")
    if token_info.minutes_detected and token_info.minutes_detected > get_max_time_by_score(token_info.score):
        problemas.append("Fora da janela de tempo")
    
    if problemas:
        print("❌ MOTIVO(S) PELO(S) QUAL(IS) NÃO COMPROU:")
        for i, problema in enumerate(problemas, 1):
            print(f"   {i}. {problema}")
    else:
        print("✅ TODAS AS VALIDAÇÕES PASSARAM!")
        print()
        print("Se o bot não comprou, pode ser:")
        print("   - Bot não está rodando")
        print("   - Erro de conexão com Jupiter API (DNS)")
        print("   - Saldo insuficiente")
        print("   - Token já foi comprado anteriormente")
        print("   - Erro ao enviar transação para Solana")
    print()
    print("="*70)

if __name__ == "__main__":
    print()
    print("Cole a mensagem do Telegram abaixo e pressione Enter:")
    print("(Ctrl+Z e Enter para finalizar)")
    print()
    
    mensagem = ""
    try:
        while True:
            linha = input()
            if linha:
                mensagem += linha + "\n"
    except EOFError:
        pass
    
    if mensagem.strip():
        diagnosticar_mensagem(mensagem.strip())
    else:
        print("Nenhuma mensagem fornecida!")











