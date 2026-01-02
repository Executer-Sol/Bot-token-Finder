"""
Utilitário para verificar saldos da carteira Solana
"""
import asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from base58 import b58decode
import config

# Endereços principais
SOL_MINT = "So11111111111111111111111111111111111111112"  # Wrapped SOL
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC

def _load_keypair() -> Keypair:
    """Load keypair from private key"""
    private_key = config.SOLANA_PRIVATE_KEY
    try:
        if isinstance(private_key, str):
            if len(private_key) == 88:  # Base58 encoded
                key_bytes = b58decode(private_key)
            elif len(private_key) == 128 or len(private_key) == 64:  # Hex
                key_bytes = bytes.fromhex(private_key.replace('0x', ''))
            else:
                key_bytes = b58decode(private_key)
        else:
            key_bytes = bytes(private_key)
        
        if len(key_bytes) == 32:
            return Keypair.from_seed(key_bytes)
        elif len(key_bytes) == 64:
            return Keypair.from_bytes(key_bytes)
        else:
            return Keypair.from_seed(key_bytes[:32])
    except Exception as e:
        raise ValueError(f"Erro ao carregar keypair: {e}")

async def get_wallet_balance() -> dict:
    """Retorna saldos da carteira (async)"""
    client = AsyncClient(config.RPC_URL)
    keypair = _load_keypair()
    wallet_address = str(keypair.pubkey())
    
    try:
        # Saldo SOL
        sol_balance = await client.get_balance(keypair.pubkey())
        sol_amount = sol_balance.value / 1e9  # Converter lamports para SOL
        
        # Saldo USDC (simplificado - retorna 0 por enquanto)
        # Para implementação completa, usar spl-token
        usdc_amount = 0.0
        
        # Conta outros tokens (simplificado)
        other_tokens_count = 0
        
        return {
            'sol': sol_amount,
            'usdc': usdc_amount,
            'wallet_address': wallet_address,
            'other_tokens_count': other_tokens_count
        }
    finally:
        await client.close()

def get_wallet_balance_sync() -> dict:
    """Retorna saldos da carteira (sync wrapper)"""
    return asyncio.run(get_wallet_balance())

