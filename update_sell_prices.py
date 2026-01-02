"""
Atualiza preços de venda dos tokens vendidos baseado em transações reais da carteira
"""
import asyncio
import aiohttp
import json
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from base58 import b58decode
import config
from typing import Dict, List, Optional
from datetime import datetime

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

async def get_sell_transactions_from_solscan(wallet_address: str, limit: int = 100) -> List[Dict]:
    """Busca transações de venda via Solscan API ou RPC direto"""
    sell_transactions = []
    
    # Tenta primeiro via Solscan API
    try:
        url = f"https://public-api.solscan.io/account/transactions"
        params = {
            'account': wallet_address,
            'limit': limit
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    transactions = data if isinstance(data, list) else data.get('data', [])
                    
                    for tx in transactions:
                        sell_info = extract_sell_info_from_solscan_tx(tx)
                        if sell_info:
                            sell_transactions.append(sell_info)
                    
                    if sell_transactions:
                        print(f"✅ Encontradas {len(sell_transactions)} vendas via Solscan API")
                        return sell_transactions
    except Exception as e:
        print(f"⚠️  Erro ao buscar via Solscan API: {e}")
    
    # Fallback: busca via RPC direto da Solana
    try:
        print("🔄 Tentando buscar transações via RPC da Solana...")
        client = AsyncClient(config.RPC_URL)
        keypair = _load_keypair()
        
        # Busca últimas transações
        signatures = await client.get_signatures_for_address(
            keypair.pubkey(),
            limit=limit
        )
        
        if signatures.value:
            for sig_info in signatures.value[:20]:  # Limita a 20 para não demorar muito
                try:
                    tx = await client.get_transaction(
                        sig_info.signature,
                        encoding="jsonParsed",
                        max_supported_transaction_version=0
                    )
                    
                    if tx.value and tx.value.transaction:
                        sell_info = await extract_sell_from_rpc_tx(tx.value, wallet_address)
                        if sell_info:
                            sell_info['signature'] = str(sig_info.signature)
                            sell_info['timestamp'] = sig_info.block_time
                            sell_transactions.append(sell_info)
                except:
                    continue
        
        await client.close()
        
        if sell_transactions:
            print(f"✅ Encontradas {len(sell_transactions)} vendas via RPC")
    except Exception as e:
        print(f"⚠️  Erro ao buscar via RPC: {e}")
    
    return sell_transactions

async def extract_sell_from_rpc_tx(tx, wallet_address: str) -> Optional[Dict]:
    """Extrai informações de venda de uma transação RPC"""
    try:
        if not hasattr(tx, 'meta') or not tx.meta:
            return None
        
        # Verifica mudança de saldo SOL (recebeu SOL = venda)
        if hasattr(tx.meta, 'pre_balances') and hasattr(tx.meta, 'post_balances'):
            pre_balance = tx.meta.pre_balances[0] if tx.meta.pre_balances else 0
            post_balance = tx.meta.post_balances[0] if tx.meta.post_balances else 0
            sol_received = (post_balance - pre_balance) / 1e9
            
            if sol_received > 0.0001:  # Recebeu pelo menos 0.0001 SOL
                # Tenta identificar o token vendido via pre/post token balances
                token_mint = None
                tokens_sold = 0
                
                if hasattr(tx.meta, 'pre_token_balances') and hasattr(tx.meta, 'post_token_balances'):
                    # Compara saldos de tokens antes e depois
                    pre_tokens = {b.mint: b.ui_token_amount.ui_amount for b in (tx.meta.pre_token_balances or []) if hasattr(b, 'mint')}
                    post_tokens = {b.mint: b.ui_token_amount.ui_amount for b in (tx.meta.post_token_balances or []) if hasattr(b, 'mint')}
                    
                    # Token que diminuiu = foi vendido
                    for mint, pre_amount in pre_tokens.items():
                        post_amount = post_tokens.get(mint, 0)
                        if pre_amount and pre_amount > post_amount:
                            token_mint = str(mint)
                            tokens_sold = pre_amount - post_amount
                            break
                
                if token_mint and tokens_sold > 0:
                    price_per_token_sol = sol_received / tokens_sold if tokens_sold > 0 else 0
                    return {
                        'token_mint': token_mint,
                        'tokens_sold': tokens_sold,
                        'sol_received': sol_received,
                        'price_per_token_sol': price_per_token_sol
                    }
    except Exception as e:
        print(f"⚠️  Erro ao extrair venda de RPC: {e}")
    
    return None

def extract_sell_info_from_solscan_tx(tx: Dict) -> Optional[Dict]:
    """Extrai informações de venda de uma transação do Solscan"""
    try:
        # Verifica se recebeu SOL (indicador de venda)
        change = tx.get('change', 0)
        if change <= 0:
            return None  # Não recebeu SOL, não é venda
        
        # Busca informações do token vendido
        token_transfers = tx.get('tokenTransfers', [])
        
        # Procura por transferência de token SAIU da carteira (venda)
        token_sold = None
        token_amount = 0
        token_mint = None
        
        for transfer in token_transfers:
            # Se o token saiu da carteira (amount negativo ou source é a carteira)
            amount = transfer.get('amount', 0)
            if amount > 0:  # Token saiu da carteira
                token_sold = transfer.get('symbol', 'UNKNOWN')
                token_mint = transfer.get('mint', '')
                # Converte amount considerando decimals
                decimals = transfer.get('decimals', 9)
                token_amount = amount / (10 ** decimals)
                break
        
        if token_sold and token_amount > 0:
            sol_received = change / 1e9  # Solscan retorna em lamports
            
            # Calcula preço por token em SOL
            price_per_token_sol = sol_received / token_amount if token_amount > 0 else 0
            
            return {
                'signature': tx.get('signature', ''),
                'timestamp': tx.get('blockTime', 0),
                'token_symbol': token_sold,
                'token_mint': token_mint,
                'tokens_sold': token_amount,
                'sol_received': sol_received,
                'price_per_token_sol': price_per_token_sol
            }
    except Exception as e:
        print(f"⚠️  Erro ao extrair info de venda: {e}")
    
    return None

async def get_sol_price_usd() -> float:
    """Busca preço atual do SOL em USD"""
    try:
        url = "https://price.jup.ag/v4/price?ids=So11111111111111111111111111111111111111112"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    price_data = data.get('data', {}).get('So11111111111111111111111111111111111111112', {})
                    return float(price_data.get('price', 150.0))
    except:
        pass
    return 150.0  # Fallback

async def update_sell_prices_from_wallet():
    """Atualiza preços de venda dos tokens vendidos baseado em transações reais"""
    try:
        # Carrega trades
        trades_file = 'trades_history.json'
        if not os.path.exists(trades_file):
            print("⚠️  Arquivo trades_history.json não encontrado")
            return
        
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades_data = json.load(f)
        
        sold_trades = trades_data.get('sold', [])
        if not sold_trades:
            print("ℹ️  Nenhum token vendido encontrado")
            return
        
        # Obtém endereço da carteira
        keypair = _load_keypair()
        wallet_address = str(keypair.pubkey())
        
        print(f"🔍 Buscando transações de venda para carteira: {wallet_address[:8]}...{wallet_address[-8:]}")
        
        # Busca transações de venda
        sell_transactions = await get_sell_transactions_from_solscan(wallet_address, limit=100)
        
        if not sell_transactions:
            print("⚠️  Nenhuma transação de venda encontrada")
            return
        
        print(f"✅ Encontradas {len(sell_transactions)} transações de venda")
        
        # Obtém preço do SOL
        sol_price_usd = await get_sol_price_usd()
        print(f"💰 Preço do SOL: ${sol_price_usd:.2f} USD")
        
        # Atualiza preços de venda
        updated_count = 0
        
        for trade in sold_trades:
            contract_address = trade.get('contract_address', '').upper()
            symbol = trade.get('symbol', '').upper()
            
            # Procura transação correspondente
            matching_tx = None
            for tx in sell_transactions:
                tx_mint = tx.get('token_mint', '').upper()
                tx_symbol = tx.get('token_symbol', '').upper()
                
                # Tenta fazer match por contract address ou symbol
                if (tx_mint == contract_address) or (tx_symbol == symbol and tx_symbol != 'UNKNOWN'):
                    matching_tx = tx
                    break
            
            if matching_tx:
                # Calcula preço de venda em USD
                price_per_token_sol = matching_tx.get('price_per_token_sol', 0)
                price_per_token_usd = price_per_token_sol * sol_price_usd
                
                # Atualiza trade
                old_price = trade.get('final_price', 0)
                trade['final_price'] = price_per_token_usd
                trade['real_sell_price_calculated'] = True
                trade['real_sol_received'] = matching_tx.get('sol_received', 0)
                trade['sell_tx_signature'] = matching_tx.get('signature', '')
                
                print(f"✅ Atualizado {symbol} ({contract_address[:8]}...):")
                print(f"   Preço antigo: ${old_price:.10f}")
                print(f"   Preço novo: ${price_per_token_usd:.10f}")
                print(f"   SOL recebido: {matching_tx.get('sol_received', 0):.6f} SOL")
                print(f"   Tokens vendidos: {matching_tx.get('tokens_sold', 0):.2f}")
                
                updated_count += 1
        
        # Salva atualizações
        if updated_count > 0:
            with open(trades_file, 'w', encoding='utf-8') as f:
                json.dump(trades_data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ {updated_count} preços de venda atualizados!")
        else:
            print("\nℹ️  Nenhum preço foi atualizado (não encontrou matches)")
            
    except Exception as e:
        import traceback
        print(f"❌ Erro ao atualizar preços de venda: {e}")
        print(traceback.format_exc())

def update_sell_prices_sync():
    """Wrapper síncrono"""
    import os
    return asyncio.run(update_sell_prices_from_wallet())

if __name__ == "__main__":
    update_sell_prices_sync()

