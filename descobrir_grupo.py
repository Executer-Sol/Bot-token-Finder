"""
Script para descobrir o ID do grupo "smart"
"""
import asyncio
from telethon import TelegramClient
import config

async def descobrir_grupo():
    """Lista grupos para encontrar o ID de 'smart'"""
    client = TelegramClient('session', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    
    await client.start(phone=config.TELEGRAM_PHONE)
    
    print("\n" + "="*70)
    print("BUSCANDO GRUPO 'smart'")
    print("="*70 + "\n")
    
    encontrado = False
    
    # Lista todos os diálogos
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            # Verifica se é o grupo "smart"
            if "smart" in dialog.name.lower() or dialog.name == "smart":
                print("GRUPO ENCONTRADO!")
                print("-"*70)
                print(f"Nome: {dialog.name}")
                print(f"ID: {dialog.id}")
                print(f"Username: {dialog.entity.username or 'N/A (grupo privado)'}")
                print(f"Tipo: {'Grupo' if dialog.is_group else 'Canal'}")
                print("-"*70)
                print(f"\nUse este ID no .env:")
                print(f"TELEGRAM_CHANNEL={dialog.id}")
                print("="*70 + "\n")
                encontrado = True
                break
    
    if not encontrado:
        print("Grupo 'smart' nao encontrado!")
        print("\nGrupos disponiveis:")
        print("-"*70)
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                print(f"Nome: {dialog.name} | ID: {dialog.id}")
        print("-"*70)
        print("\nDica: Verifique se:")
        print("   1. O bot esta no grupo")
        print("   2. O nome do grupo esta correto")
        print("   3. O bot tem permissao para ver o grupo")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(descobrir_grupo())

