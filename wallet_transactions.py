"""
Busca transações de venda da carteira para calcular preços reais de venda
"""
import asyncio
import aiohttp
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from base58 import b58decode
import config
from typing import List, Dict, Optional
from datetime import datetime

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

async def get_sell_transactions(limit: int = 50) -> List[Dict]:
    """Busca transações de venda da carteira
    Retorna lista de transações com informações de venda
    """
    client = AsyncClient(config.RPC_URL)
    keypair = _load_keypair()
    wallet_address = str(keypair.pubkey())
    
    sell_transactions = []
    
    try:
        # Busca últimas transações da carteira
        signatures = await client.get_signatures_for_address(
            keypair.pubkey(),
            limit=limit
        )
        
        if not signatures.value:
            return []
        
        # Para cada assinatura, busca detalhes da transação
        for sig_info in signatures.value:
            try:
                tx_sig = sig_info.signature
                
                # Busca detalhes da transação
                tx = await client.get_transaction(
                    tx_sig,
                    encoding="jsonParsed",
                    max_supported_transaction_version=0
                )
                
                if not tx.value or not tx.value.transaction:
                    continue
                
                # Analisa a transação para identificar vendas
                sell_info = await analyze_transaction_for_sell(tx.value, wallet_address)
                
                if sell_info:
                    sell_info['signature'] = str(tx_sig)
                    sell_info['timestamp'] = sig_info.block_time
                    sell_transactions.append(sell_info)
                    
            except Exception as e:
                print(f"⚠️  Erro ao processar transação {sig_info.signature}: {e}")
                continue
                
    finally:
        await client.close()
    
    return sell_transactions

async def analyze_transaction_for_sell(tx, wallet_address: str) -> Optional[Dict]:
    """Analisa uma transação para identificar se foi uma venda de token
    Retorna informações sobre a venda se encontrada
    """
    try:
        # Verifica se a transação tem instruções de swap
        if not hasattr(tx, 'transaction') or not hasattr(tx.transaction, 'message'):
            return None
        
        message = tx.transaction.message
        
        # Busca por instruções de swap (Jupiter, Raydium, etc)
        # Verifica se houve transferência de tokens para a carteira (recebeu SOL)
        
        # Tenta extrair informações dos logs
        if hasattr(tx, 'meta') and tx.meta and hasattr(tx.meta, 'log_messages'):
            logs = tx.meta.log_messages or []
            
            # Procura por padrões de swap
            for log in logs:
                if 'swap' in log.lower() or 'jupiter' in log.lower():
                    # Encontrou swap, tenta extrair valores
                    return await extract_sell_info_from_tx(tx, wallet_address)
        
        # Tenta extrair informações das mudanças de saldo
        if hasattr(tx, 'meta') and tx.meta and hasattr(tx.meta, 'pre_balances') and hasattr(tx.meta, 'post_balances'):
            pre_balance = tx.meta.pre_balances[0] if tx.meta.pre_balances else 0
            post_balance = tx.meta.post_balances[0] if tx.meta.post_balances else 0
            
            # Se o saldo aumentou, pode ser uma venda
            sol_received = (post_balance - pre_balance) / 1e9
            
            if sol_received > 0.0001:  # Recebeu pelo menos 0.0001 SOL
                # Busca informações do token vendido
                token_info = await extract_token_info_from_tx(tx, wallet_address)
                
                if token_info:
                    return {
                        'type': 'sell',
                        'sol_received': sol_received,
                        'token_mint': token_info.get('mint'),
                        'token_symbol': token_info.get('symbol', 'UNKNOWN'),
                        'tokens_sold': token_info.get('amount', 0),
                        'price_per_token_sol': sol_received / token_info.get('amount', 1) if token_info.get('amount', 0) > 0 else 0
                    }
        
    except Exception as e:
        print(f"⚠️  Erro ao analisar transação: {e}")
    
    return None

async def extract_sell_info_from_tx(tx, wallet_address: str) -> Optional[Dict]:
    """Extrai informações de venda de uma transação"""
    try:
        # Implementação simplificada - busca mudanças de saldo
        if hasattr(tx, 'meta') and tx.meta:
            pre_balance = tx.meta.pre_balances[0] if tx.meta.pre_balances else 0
            post_balance = tx.meta.post_balances[0] if tx.meta.post_balances else 0
            sol_received = (post_balance - pre_balance) / 1e9
            
            if sol_received > 0:
                token_info = await extract_token_info_from_tx(tx, wallet_address)
                return {
                    'type': 'sell',
                    'sol_received': sol_received,
                    'token_mint': token_info.get('mint') if token_info else None,
                    'token_symbol': token_info.get('symbol', 'UNKNOWN') if token_info else 'UNKNOWN',
                    'tokens_sold': token_info.get('amount', 0) if token_info else 0
                }
    except:
        pass
    return None

async def extract_token_info_from_tx(tx, wallet_address: str) -> Optional[Dict]:
    """Extrai informações do token vendido da transação"""
    try:
        # Tenta extrair do innerInstructions ou pre/post token balances
        if hasattr(tx, 'meta') and tx.meta:
            # Busca por inner instructions que podem ter informações do token
            if hasattr(tx.meta, 'inner_instructions') and tx.meta.inner_instructions:
                for inner in tx.meta.inner_instructions:
                    # Procura por transferências de tokens
                    if hasattr(inner, 'instructions'):
                        for inst in inner.instructions:
                            # Tenta extrair mint address e quantidade
                            pass  # Implementação mais complexa seria necessária aqui
    except:
        pass
    return None

async def get_sell_price_from_solscan(contract_address: str, wallet_address: str) -> Optional[float]:
    """Busca preço de venda via Solscan API"""
    try:
        # Busca transações da carteira no Solscan
        url = f"https://api.solscan.io/account/transactions?account={wallet_address}&limit=50"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    transactions = data.get('data', [])
                    
                    # Procura por transações que envolvem o token
                    for tx in transactions:
                        # Verifica se é uma venda (recebeu SOL)
                        # Implementação específica do Solscan seria necessária aqui
                        pass
    except:
        pass
    return None

def get_sell_transactions_sync(limit: int = 50) -> List[Dict]:
    """Wrapper síncrono"""
    return asyncio.run(get_sell_transactions(limit))










