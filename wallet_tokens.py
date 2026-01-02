"""
Busca tokens SPL da carteira e calcula valores via Jupiter API
"""
import asyncio
import aiohttp
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from base58 import b58decode
import config
from typing import List, Dict, Optional

SOL_MINT = "So11111111111111111111111111111111111111112"

def _load_keypair() -> Keypair:
    """Load keypair from private key"""
    private_key = config.SOLANA_PRIVATE_KEY
    try:
        if isinstance(private_key, str):
            if len(private_key) == 88:
                key_bytes = b58decode(private_key)
            elif len(private_key) == 128 or len(private_key) == 64:
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

async def get_wallet_tokens() -> List[Dict]:
    """Busca todos os tokens SPL da carteira e calcula valores via Jupiter"""
    client = AsyncClient(config.RPC_URL)
    keypair = _load_keypair()
    wallet_address = str(keypair.pubkey())
    
    tokens = []
    
    try:
        # NÃO adiciona SOL aqui - ele já é mostrado na seção de saldos
        # Busca apenas tokens SPL (não SOL)
        
        # Busca tokens SPL usando getParsedTokenAccountsByOwner
        try:
            from solders.pubkey import Pubkey
            
            # Token Program ID
            token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            # Busca contas de tokens (método correto para AsyncClient)
            response = await client.get_parsed_token_accounts_by_owner(
                keypair.pubkey(),
                token_program_id
            )
            
            if response and hasattr(response, 'value') and response.value:
                # Busca preços de todos os tokens de uma vez (mais eficiente)
                token_mints = []
                for account_info in response.value:
                    parsed_info = account_info.account.data.parsed.get('info', {})
                    mint = parsed_info.get('mint')
                    if mint and mint != SOL_MINT:
                        token_mints.append(mint)
                
                # Busca preços em batch
                prices = await get_token_prices_batch(token_mints)
                
                # Processa cada token
                for account_info in response.value:
                    parsed_info = account_info.account.data.parsed.get('info', {})
                    mint = parsed_info.get('mint')
                    token_amount = parsed_info.get('tokenAmount', {})
                    
                    if not mint or mint == SOL_MINT:
                        continue
                    
                    amount = float(token_amount.get('uiAmount', 0))
                    decimals = token_amount.get('decimals', 0)
                    
                    if amount <= 0:
                        continue
                    
                    # Busca preço do token
                    price_usd = prices.get(mint, 0)
                    value_usd = amount * price_usd if price_usd else 0
                    
                    # Busca informações do token (símbolo, nome)
                    token_info = await get_token_info(mint)
                    
                    tokens.append({
                        'mint': mint,
                        'symbol': token_info.get('symbol', 'UNKNOWN'),
                        'name': token_info.get('name', 'Unknown Token'),
                        'amount': amount,
                        'decimals': decimals,
                        'price_usd': price_usd,
                        'value_usd': value_usd,
                        'logo_uri': token_info.get('logoURI')
                    })
        except Exception as e:
            print(f"⚠️  Erro ao buscar tokens SPL: {e}")
        
        # Ordena por valor (maior primeiro)
        tokens.sort(key=lambda x: x['value_usd'], reverse=True)
        
        return tokens
        
    finally:
        await client.close()

async def get_token_price(token_mint: str) -> Optional[float]:
    """Busca preço de um token via Jupiter Price API"""
    try:
        url = f"https://price.jup.ag/v4/price?ids={token_mint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    price_data = data.get('data', {}).get(token_mint, {})
                    return float(price_data.get('price', 0))
    except:
        pass
    return None

async def get_token_prices_batch(token_mints: List[str]) -> Dict[str, float]:
    """Busca preços de múltiplos tokens de uma vez"""
    if not token_mints:
        return {}
    
    prices = {}
    
    try:
        # Jupiter API permite até 100 tokens por request
        batch_size = 100
        for i in range(0, len(token_mints), batch_size):
            batch = token_mints[i:i+batch_size]
            ids = ','.join(batch)
            
            url = f"https://price.jup.ag/v4/price?ids={ids}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        price_data = data.get('data', {})
                        for mint, info in price_data.items():
                            prices[mint] = float(info.get('price', 0))
    except Exception as e:
        print(f"⚠️  Erro ao buscar preços em batch: {e}")
    
    return prices

async def get_token_info(token_mint: str) -> Dict:
    """Busca informações do token (símbolo, nome) via Jupiter Token List"""
    try:
        # Tenta buscar da Jupiter Token List
        url = "https://token.jup.ag/all"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    tokens = await response.json()
                    for token in tokens:
                        if token.get('address') == token_mint:
                            return {
                                'symbol': token.get('symbol', 'UNKNOWN'),
                                'name': token.get('name', 'Unknown Token'),
                                'logoURI': token.get('logoURI')
                            }
    except:
        pass
    
    # Fallback: retorna informações básicas
    return {
        'symbol': 'UNKNOWN',
        'name': 'Unknown Token',
        'logoURI': None
    }

def get_wallet_tokens_sync() -> List[Dict]:
    """Wrapper síncrono"""
    return asyncio.run(get_wallet_tokens())

