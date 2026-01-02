"""
Script para listar grupos e descobrir o ID do grupo "smart"
"""
import asyncio
from telethon import TelegramClient
import config

async def list_groups():
    """Lista todos os grupos para encontrar o ID de 'smart'"""
    client = TelegramClient('session', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    
    await client.start(phone=config.TELEGRAM_PHONE)
    print("\n" + "="*70)
    print("GRUPOS E CANAIS DISPONÍVEIS")
    print("="*70 + "\n")
    
    # Lista todos os diálogos (chats, grupos, canais)
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f"Nome: {dialog.name}")
            print(f"ID: {dialog.id}")
            print(f"Username: {dialog.entity.username or 'N/A'}")
            print(f"Tipo: {'Grupo' if dialog.is_group else 'Canal'}")
            print("-" * 70)
    
    print("\n" + "="*70)
    print("INSTRUÇÕES:")
    print("="*70)
    print("1. Encontre o grupo 'smart' na lista acima")
    print("2. Copie o ID (número, pode ser negativo)")
    print("3. Use esse ID no .env assim:")
    print("   TELEGRAM_CHANNEL=-1001234567890")
    print("   (ou apenas o número, o Telethon aceita ambos)")
    print("="*70 + "\n")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_groups())

