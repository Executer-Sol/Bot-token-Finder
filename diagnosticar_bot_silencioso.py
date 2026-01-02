"""
Diagnóstico: Por que o bot não mostra nada no terminal?
"""
import asyncio
import sys
import io
from telethon import TelegramClient, events
from message_parser import parse_token_message
import config
from bot_control import get_bot_state
from logger import log_info, log_warning, log_error, log_success

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def diagnosticar_bot_silencioso():
    """Diagnostica por que o bot não mostra nada"""
    print("="*70)
    print("🔍 DIAGNÓSTICO: Bot Não Mostra Nada no Terminal")
    print("="*70)
    print()
    
    # 1. Verifica estado do bot
    print("1️⃣ ESTADO DO BOT")
    print("-"*70)
    bot_enabled = get_bot_state()
    if bot_enabled:
        print("✅ Bot está ATIVO")
    else:
        print("❌ Bot está DESATIVADO!")
        print("   Solução: Ative na interface web (http://localhost:5000)")
    print()
    
    # 2. Testa conexão Telegram
    print("2️⃣ TESTE DE CONEXÃO TELEGRAM")
    print("-"*70)
    client = TelegramClient(
        'session',
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH
    )
    
    try:
        print("📱 Conectando...")
        await client.start(phone=config.TELEGRAM_PHONE)
        print("✅ Conectado ao Telegram!")
        print()
        
        # 3. Busca canal
        print("3️⃣ BUSCANDO CANAL")
        print("-"*70)
        target_chat_id = None
        target_chat_name = config.TELEGRAM_CHANNEL
        
        try:
            if config.TELEGRAM_CHANNEL.lstrip('-').isdigit():
                target_chat_id = int(config.TELEGRAM_CHANNEL)
                target_chat = await client.get_entity(target_chat_id)
                target_chat_name = target_chat.title if hasattr(target_chat, 'title') else str(target_chat_id)
                print(f"✅ Canal encontrado: {target_chat_name} (ID: {target_chat_id})")
            else:
                async for dialog in client.iter_dialogs():
                    if dialog.name.lower() == config.TELEGRAM_CHANNEL.lower():
                        target_chat_id = dialog.id
                        target_chat_name = dialog.name
                        print(f"✅ Canal encontrado: {dialog.name} (ID: {dialog.id})")
                        break
        except Exception as e:
            print(f"❌ Erro ao buscar canal: {e}")
            await client.disconnect()
            return
        
        if not target_chat_id:
            print(f"❌ Canal '{config.TELEGRAM_CHANNEL}' não encontrado!")
            await client.disconnect()
            return
        
        print()
        
        # 4. Monitora mensagens e testa parse
        print("4️⃣ TESTE DE DETECÇÃO DE TOKENS")
        print("-"*70)
        print("Monitorando canal por 60 segundos...")
        print("Envie uma mensagem com formato de token no canal!")
        print()
        
        mensagens_recebidas = 0
        tokens_detectados = 0
        
        @client.on(events.NewMessage(chats=target_chat_id))
        async def handler(event):
            nonlocal mensagens_recebidas, tokens_detectados
            mensagens_recebidas += 1
            message_text = event.message.text or "[Sem texto]"
            
            print(f"📨 Mensagem #{mensagens_recebidas} recebida")
            print(f"   Texto completo ({len(message_text)} caracteres):")
            print(f"   {message_text}")
            print()
            
            # Testa parse
            token_info = parse_token_message(message_text)
            if token_info:
                tokens_detectados += 1
                print(f"   ✅ TOKEN DETECTADO!")
                print(f"      Símbolo: {token_info.symbol}")
                print(f"      Score: {token_info.score}")
                print(f"      CA: {token_info.contract_address}")
                print()
                print(f"   🔍 Simulando processamento do bot...")
                
                # Simula o que o bot faria
                if not bot_enabled:
                    print(f"      ⚠️  Bot está DESATIVADO - não processaria")
                else:
                    amount_sol = config.get_amount_by_score(token_info.score)
                    if amount_sol == 0:
                        print(f"      ⚠️  Score {token_info.score} sem valor configurado - não processaria")
                    else:
                        max_time = config.get_max_time_by_score(token_info.score)
                        if token_info.minutes_detected and token_info.minutes_detected > max_time:
                            print(f"      ⚠️  Fora da janela de tempo ({token_info.minutes_detected}min > {max_time}min) - não processaria")
                        else:
                            print(f"      ✅ Bot DEVERIA processar e mostrar no terminal!")
                            print(f"      ✅ Bot DEVERIA tentar comprar!")
            else:
                print(f"   ⚠️  Não é formato de token (bot ignora)")
            print()
        
        await asyncio.sleep(60)
        
        print()
        print("="*70)
        print("📊 RESULTADO DO DIAGNÓSTICO")
        print("="*70)
        print(f"   Mensagens recebidas: {mensagens_recebidas}")
        print(f"   Tokens detectados: {tokens_detectados}")
        print()
        
        if mensagens_recebidas == 0:
            print("❌ PROBLEMA: Bot não está recebendo mensagens!")
            print()
            print("Possíveis motivos:")
            print("   1. Canal não está enviando mensagens")
            print("   2. Bot não tem acesso ao canal")
            print("   3. ID do canal incorreto")
        elif tokens_detectados == 0:
            print("⚠️  Bot está recebendo mensagens, mas nenhuma tem formato de token")
            print()
            print("Verifique se as mensagens têm:")
            print("   - #símbolo")
            print("   - Score: X")
            print("   - CA: endereço")
            print("   - $preço")
        else:
            print("✅ Bot está funcionando!")
            print()
            print("Se o bot não mostra no terminal quando roda normalmente:")
            print("   1. Verifique se o bot está rodando (python run_all.py)")
            print("   2. Verifique os logs: Get-Content logs\\bot_*.log -Tail 50")
            print("   3. Verifique se bot está ATIVO na interface web")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        try:
            await client.disconnect()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(diagnosticar_bot_silencioso())

