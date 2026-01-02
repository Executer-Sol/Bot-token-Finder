#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista todos os chats/grupos do Telegram com seus IDs"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from telethon import TelegramClient
import config

async def listar_chats():
    print("=" * 70)
    print("📋 LISTA DE CHATS/GRUPOS DO TELEGRAM")
    print("=" * 70)
    print()
    
    client = TelegramClient('session', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    
    try:
        await client.start(phone=config.TELEGRAM_PHONE)
        print("✅ Conectado ao Telegram!")
        print()
        
        print("🔍 Buscando todos os chats/grupos...")
        print()
        print("-" * 70)
        print(f"{'Nome':<40} {'ID':<20} {'Tipo'}")
        print("-" * 70)
        
        chats_encontrados = []
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                tipo = "Grupo" if dialog.is_group else "Canal"
                nome = dialog.name
                chat_id = dialog.id
                
                # Destaca o chat "smart" se for ele
                destaque = ""
                if str(chat_id) == str(config.TELEGRAM_CHANNEL) or nome.lower() == "smart":
                    destaque = " ⭐ (MONITORADO)"
                
                print(f"{nome:<40} {chat_id:<20} {tipo}{destaque}")
                chats_encontrados.append({
                    'nome': nome,
                    'id': chat_id,
                    'tipo': tipo
                })
        
        print("-" * 70)
        print()
        print(f"✅ Total de chats encontrados: {len(chats_encontrados)}")
        print()
        
        # Mostra o chat configurado
        print("=" * 70)
        print("📌 CHAT CONFIGURADO NO BOT:")
        print("=" * 70)
        print(f"   TELEGRAM_CHANNEL: {config.TELEGRAM_CHANNEL}")
        
        # Procura o chat configurado na lista
        chat_configurado = None
        for chat in chats_encontrados:
            if str(chat['id']) == str(config.TELEGRAM_CHANNEL) or chat['nome'].lower() == config.TELEGRAM_CHANNEL.lower():
                chat_configurado = chat
                break
        
        if chat_configurado:
            print(f"   ✅ Chat encontrado: {chat_configurado['nome']} (ID: {chat_configurado['id']})")
        else:
            print(f"   ⚠️  Chat não encontrado na lista!")
            print(f"   💡 Verifique se o ID está correto ou se você tem acesso ao chat")
        
        print()
        print("=" * 70)
        print("💡 DICA:")
        print("   O bot deve monitorar APENAS o chat 'smart'")
        print("   Se aparecer mensagens de outros chats, verifique o ID configurado")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(listar_chats())










