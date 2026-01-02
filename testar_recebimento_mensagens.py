"""
Teste: Verifica se o bot está recebendo mensagens do Telegram
"""
import asyncio
import sys
import io
from telethon import TelegramClient, events
import config

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def testar_recebimento():
    """Testa se o bot recebe mensagens do canal"""
    print("="*70)
    print("🔍 TESTE: Recebimento de Mensagens do Telegram")
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
        print("👂 MONITORANDO MENSAGENS...")
        print(f"   Canal: {target_chat_name}")
        print("   Pressione Ctrl+C para parar")
        print("="*70)
        print()
        
        mensagens_recebidas = 0
        
        @client.on(events.NewMessage(chats=target_chat_id))
        async def handler(event):
            nonlocal mensagens_recebidas
            mensagens_recebidas += 1
            message_text = event.message.text or "[Sem texto]"
            preview = message_text[:100] if len(message_text) > 100 else message_text
            print(f"📨 Mensagem #{mensagens_recebidas} recebida:")
            print(f"   {preview}")
            print()
            
            # Verifica se tem formato de token
            if '#' in message_text and 'Score:' in message_text and 'CA:' in message_text:
                print("   ✅ FORMATO DE TOKEN DETECTADO!")
                print()
        
        print("⏳ Aguardando mensagens... (60 segundos)")
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
            print("   1. O canal não está enviando mensagens agora")
            print("   2. O bot não tem permissão para ler mensagens")
            print("   3. O ID do canal está incorreto")
            print("   4. Problema de conexão com Telegram")
            print()
            print("💡 Soluções:")
            print("   - Verifique se o canal está enviando mensagens")
            print("   - Verifique se o bot tem acesso ao canal")
            print("   - Tente rodar novamente quando houver mensagens")
        else:
            print("✅ SUCESSO: Bot está recebendo mensagens!")
            print()
            print("Se o bot não está detectando tokens, o problema pode ser:")
            print("   - Formato da mensagem diferente do esperado")
            print("   - Mensagens não têm formato de token (sem #, Score, CA)")
            
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
    asyncio.run(testar_recebimento())











