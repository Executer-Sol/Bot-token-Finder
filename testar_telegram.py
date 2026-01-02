#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa conexão e detecção de mensagens do Telegram"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from telethon import TelegramClient
from telethon import events
import config
from message_parser import parse_token_message

async def test_telegram():
    print("=" * 70)
    print("🔍 TESTE DE CONEXÃO E DETECÇÃO DO TELEGRAM")
    print("=" * 70)
    print()
    
    # 1. Verifica configuração
    print("1️⃣  VERIFICANDO CONFIGURAÇÃO:")
    print(f"   TELEGRAM_API_ID: {'✅ Configurado' if config.TELEGRAM_API_ID else '❌ NÃO CONFIGURADO'}")
    print(f"   TELEGRAM_API_HASH: {'✅ Configurado' if config.TELEGRAM_API_HASH else '❌ NÃO CONFIGURADO'}")
    print(f"   TELEGRAM_PHONE: {'✅ Configurado' if config.TELEGRAM_PHONE else '❌ NÃO CONFIGURADO'}")
    print(f"   TELEGRAM_CHANNEL: {config.TELEGRAM_CHANNEL if config.TELEGRAM_CHANNEL else '❌ NÃO CONFIGURADO'}")
    print()
    
    if not all([config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH, config.TELEGRAM_PHONE]):
        print("❌ Configuração incompleta! Verifique o arquivo .env")
        return
    
    # 2. Conecta ao Telegram
    print("2️⃣  CONECTANDO AO TELEGRAM...")
    client = TelegramClient('session', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    
    try:
        await client.start(phone=config.TELEGRAM_PHONE)
        print("✅ Conectado ao Telegram!")
        print()
        
        # 3. Busca o canal
        print("3️⃣  BUSCANDO CANAL/GRUPO...")
        target_chat_id = None
        target_chat_name = config.TELEGRAM_CHANNEL
        
        try:
            if config.TELEGRAM_CHANNEL.lstrip('-').isdigit():
                target_chat_id = int(config.TELEGRAM_CHANNEL)
                target_chat = await client.get_entity(target_chat_id)
                target_chat_name = target_chat.title if hasattr(target_chat, 'title') else str(target_chat_id)
                print(f"✅ Canal encontrado por ID: {target_chat_name} (ID: {target_chat_id})")
            else:
                async for dialog in client.iter_dialogs():
                    if dialog.name.lower() == config.TELEGRAM_CHANNEL.lower() or dialog.name == config.TELEGRAM_CHANNEL:
                        target_chat_id = dialog.id
                        target_chat_name = dialog.name
                        print(f"✅ Canal encontrado: {dialog.name} (ID: {dialog.id})")
                        break
                
                if not target_chat_id:
                    if config.TELEGRAM_CHANNEL.startswith('@'):
                        target_chat = await client.get_entity(config.TELEGRAM_CHANNEL)
                        target_chat_id = target_chat.id
                        target_chat_name = target_chat.title if hasattr(target_chat, 'title') else config.TELEGRAM_CHANNEL
                        print(f"✅ Canal encontrado por username: {target_chat_name} (ID: {target_chat_id})")
        except Exception as e:
            print(f"❌ Erro ao buscar canal: {e}")
            print()
            print("📋 Grupos disponíveis:")
            count = 0
            async for dialog in client.iter_dialogs():
                if (dialog.is_group or dialog.is_channel) and count < 10:
                    print(f"   - {dialog.name} (ID: {dialog.id})")
                    count += 1
            return
        
        if not target_chat_id:
            print("❌ Canal não encontrado!")
            return
        
        print()
        
        # 4. Testa parser com mensagem de exemplo
        print("4️⃣  TESTANDO PARSER DE MENSAGENS...")
        test_message = """#TESTE ● $0.0₃62 62K FDV atualmente

Score: 15 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 3pts)

CA: A6RTAd1iXnQqAEKpnLtnDL3uaczevoicafDEVzExpump"""
        
        token_info = parse_token_message(test_message)
        if token_info:
            print("✅ Parser funcionando!")
            print(f"   Símbolo: {token_info.symbol}")
            print(f"   Score: {token_info.score}")
            print(f"   CA: {token_info.contract_address}")
        else:
            print("❌ Parser falhou!")
        print()
        
        # 5. Monitora mensagens por 30 segundos
        print("5️⃣  MONITORANDO MENSAGENS (30 segundos)...")
        print("   Envie uma mensagem no canal agora!")
        print()
        
        messages_received = []
        
        @client.on(events.NewMessage(chats=target_chat_id, incoming=True))
        async def handler(event):
            message_text = event.message.text
            if message_text:
                messages_received.append(message_text)
                print(f"📨 Mensagem recebida ({len(message_text)} chars):")
                print(f"   {message_text[:200]}...")
                print()
                
                # Testa parse
                token_info = parse_token_message(message_text)
                if token_info:
                    print(f"✅ Token detectado: {token_info.symbol} (Score: {token_info.score})")
                else:
                    print("⚠️  Mensagem não é um token ou parse falhou")
                print()
        
        # Aguarda 30 segundos
        await asyncio.sleep(30)
        
        print()
        print("=" * 70)
        if messages_received:
            print(f"✅ {len(messages_received)} mensagem(ns) recebida(s)!")
        else:
            print("❌ Nenhuma mensagem recebida!")
            print()
            print("💡 Possíveis causas:")
            print("   - Bot não tem permissão para ler mensagens do canal")
            print("   - Canal é privado e bot não está adicionado")
            print("   - Nenhuma mensagem foi enviada durante o teste")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(test_telegram())










