"""
Teste: Verifica se o bot vê TODAS as mensagens (não só tokens)
"""
import asyncio
import sys
import io
from telethon import TelegramClient, events
import config

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def testar_todas_mensagens():
    """Testa se o bot vê todas as mensagens do canal"""
    print("="*70)
    print("🔍 TESTE: Bot vê TODAS as mensagens?")
    print("="*70)
    print()
    
    client = TelegramClient(
        'session',
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH
    )
    
    try:
        print("📱 Conectando ao Telegram...")
        await client.start(phone=config.TELEGRAM_PHONE)
        print("✅ Conectado!")
        print()
        
        # Busca o canal
        target_chat_id = None
        target_chat_name = config.TELEGRAM_CHANNEL
        
        print(f"🔍 Buscando canal: {config.TELEGRAM_CHANNEL}")
        
        try:
            if config.TELEGRAM_CHANNEL.lstrip('-').isdigit():
                target_chat_id = int(config.TELEGRAM_CHANNEL)
                target_chat = await client.get_entity(target_chat_id)
                target_chat_name = target_chat.title if hasattr(target_chat, 'title') else str(target_chat_id)
                print(f"✅ Canal encontrado por ID: {target_chat_name} (ID: {target_chat_id})")
            else:
                async for dialog in client.iter_dialogs():
                    if dialog.name.lower() == config.TELEGRAM_CHANNEL.lower():
                        target_chat_id = dialog.id
                        target_chat_name = dialog.name
                        print(f"✅ Canal encontrado: {dialog.name} (ID: {dialog.id})")
                        break
        except Exception as e:
            print(f"❌ Erro ao buscar canal: {e}")
            return
        
        if not target_chat_id:
            print(f"❌ Canal '{config.TELEGRAM_CHANNEL}' não encontrado!")
            return
        
        print()
        print("="*70)
        print("👂 MONITORANDO TODAS AS MENSAGENS...")
        print(f"   Canal: {target_chat_name}")
        print("   Este teste mostra TODAS as mensagens (não só tokens)")
        print("   Pressione Ctrl+C para parar")
        print("="*70)
        print()
        
        mensagens_recebidas = 0
        
        @client.on(events.NewMessage(chats=target_chat_id))
        async def handler(event):
            nonlocal mensagens_recebidas
            mensagens_recebidas += 1
            message_text = event.message.text or "[Sem texto]"
            sender = await event.get_sender()
            sender_name = sender.first_name if sender else "Desconhecido"
            
            print(f"📨 Mensagem #{mensagens_recebidas} recebida:")
            print(f"   De: {sender_name}")
            print(f"   Texto: {message_text[:200]}")
            
            # Verifica se tem formato de token
            from message_parser import parse_token_message
            token_info = parse_token_message(message_text)
            if token_info:
                print(f"   ✅ FORMATO DE TOKEN DETECTADO!")
                print(f"      Símbolo: {token_info.symbol}")
                print(f"      Score: {token_info.score}")
            else:
                print(f"   ⚠️  Não é formato de token (bot ignora)")
            print()
        
        print("⏳ Aguardando mensagens... (60 segundos)")
        print("   Envie uma mensagem de teste no canal agora!")
        print()
        
        # Aguarda 60 segundos
        await asyncio.sleep(60)
        
        print()
        print("="*70)
        print("📊 RESULTADO DO TESTE")
        print("="*70)
        print(f"   Total de mensagens recebidas: {mensagens_recebidas}")
        print()
        
        if mensagens_recebidas == 0:
            print("❌ PROBLEMA: Nenhuma mensagem foi recebida!")
            print()
            print("Possíveis motivos:")
            print("   1. Você não enviou mensagem no canal")
            print("   2. Você não tem permissão para enviar no canal")
            print("   3. Bot não tem acesso ao canal")
        else:
            print("✅ SUCESSO: Bot está recebendo mensagens!")
            print()
            print("💡 IMPORTANTE:")
            print("   - Bot RECEBE todas as mensagens")
            print("   - Bot só PROCESSA mensagens com formato de token")
            print("   - Mensagens normais são ignoradas (não aparecem no terminal)")
            
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("\n✅ Desconectado do Telegram")

if __name__ == "__main__":
    asyncio.run(testar_todas_mensagens())











