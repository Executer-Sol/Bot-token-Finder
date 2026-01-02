import asyncio
import aiohttp
import json
import base64
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned
from solana.rpc.async_api import AsyncClient
from base58 import b58decode
import config
from typing import Optional, Dict

# Endereços
SOL_MINT = "So11111111111111111111111111111111111111112"  # Wrapped SOL

class JupiterClient:
    def __init__(self):
        self.rpc_url = config.RPC_URL
        self.private_key = config.SOLANA_PRIVATE_KEY
        self.slippage_bps = config.SLIPPAGE_BPS
        # Garante que está usando RPC da Alchemy (mais confiável)
        if 'alchemy.com' not in self.rpc_url.lower():
            print(f"⚠️  RPC não é da Alchemy. Recomendado usar Alchemy RPC para melhor performance.")
            print(f"   RPC atual: {self.rpc_url}")
        else:
            print(f"✅ Usando RPC da Alchemy: {self.rpc_url.split('/v2/')[0]}/v2/***")
        self.client = AsyncClient(self.rpc_url)
        self.keypair = self._load_keypair()
    
    def _load_keypair(self) -> Keypair:
        """Load keypair from private key"""
        try:
            if isinstance(self.private_key, str):
                if len(self.private_key) == 88:  # Base58 encoded
                    key_bytes = b58decode(self.private_key)
                elif len(self.private_key) == 128 or len(self.private_key) == 64:  # Hex
                    key_bytes = bytes.fromhex(self.private_key.replace('0x', ''))
                else:
                    key_bytes = b58decode(self.private_key)
            else:
                key_bytes = bytes(self.private_key)
            
            if len(key_bytes) == 32:
                return Keypair.from_seed(key_bytes)
            elif len(key_bytes) == 64:
                return Keypair.from_bytes(key_bytes)
            else:
                return Keypair.from_seed(key_bytes[:32])
        except Exception as e:
            raise ValueError(f"Erro ao carregar keypair: {e}")
    
    async def get_quote(self, input_mint: str, output_mint: str, amount: int, slippage_bps: int = None, max_retries: int = 3):
        """Get swap quote from Jupiter with retry and alternative endpoints"""
        slippage = slippage_bps or self.slippage_bps
        
        # Usa novos endpoints da Jupiter API (quote-api.jup.ag foi descontinuado)
        # Novo endpoint: api.jup.ag/swap/v1/quote
        urls = [
            "https://api.jup.ag/swap/v1/quote",    # Novo endpoint oficial
            "https://quote-api.jup.ag/v6/quote"   # Fallback (pode não funcionar)
        ]
        
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage,
            "onlyDirectRoutes": "false",
            "asLegacyTransaction": "false"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        if hasattr(config, 'JUPITER_API_KEY') and config.JUPITER_API_KEY:
            headers["x-api-key"] = config.JUPITER_API_KEY
        
        last_error = None
        for url in urls:
            for attempt in range(max_retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(url, params=params, headers=headers) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                error_text = await response.text()
                                last_error = Exception(f"Erro ao obter quote: {response.status} - {error_text}")
                except aiohttp.ClientConnectorError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Backoff
                    continue
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))
                    continue
        
        raise Exception(f"Erro ao obter quote após {max_retries} tentativas: {last_error}")
    
    async def swap(self, quote: dict, use_sol: bool = True, max_retries: int = 3) -> str:
        """Execute swap using Jupiter API with retry and alternative endpoints
        Args:
            quote: Quote response from get_quote
            use_sol: True para SOL (wrap/unwrap), False para tokens SPL
        """
        # Usa novos endpoints da Jupiter API
        urls = [
            "https://api.jup.ag/swap/v1/swap",    # Novo endpoint oficial
            "https://quote-api.jup.ag/v6/swap"   # Fallback (pode não funcionar)
        ]
        
        payload = {
            "quoteResponse": quote,
            "userPublicKey": str(self.keypair.pubkey()),
            "wrapUnwrapSOL": use_sol,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": "auto"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if hasattr(config, 'JUPITER_API_KEY') and config.JUPITER_API_KEY:
            headers["x-api-key"] = config.JUPITER_API_KEY
        
        last_error = None
        for url in urls:
            for attempt in range(max_retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=15)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(url, json=payload, headers=headers) as response:
                            if response.status == 200:
                                swap_transaction = await response.json()
                                return swap_transaction['swapTransaction']
                            else:
                                error_text = await response.text()
                                last_error = Exception(f"Erro ao executar swap: {response.status} - {error_text}")
                except aiohttp.ClientConnectorError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Backoff
                    continue
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))
                    continue
        
        raise Exception(f"Erro ao executar swap após {max_retries} tentativas: {last_error}")
    
    async def send_transaction(self, transaction_hex: str) -> str:
        """Send transaction to Solana network"""
        try:
            transaction_bytes = base64.b64decode(transaction_hex)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Assina a mensagem da transação usando to_bytes_versioned (método recomendado)
            message_bytes = to_bytes_versioned(transaction.message)
            signature = self.keypair.sign_message(message_bytes)
            
            # Cria uma nova transação populada com a assinatura usando populate
            signed_transaction = VersionedTransaction.populate(transaction.message, [signature])
            
            # Envia a transação assinada
            result = await self.client.send_transaction(signed_transaction)
            return str(result.value)
        except Exception as e:
            error_str = str(e)
            # Melhora mensagem de erro para erros comuns
            if "0x6" in error_str or "Custom(6)" in error_str:
                raise Exception(f"Erro ao enviar transação: Falha no swap (erro 0x6 - possível problema de liquidez, slippage ou token inválido). Detalhes: {error_str[:200]}")
            elif "0x1771" in error_str or "Custom(6001)" in error_str:
                raise Exception(f"Erro ao enviar transação: Slippage muito alto ou quantidade insuficiente (erro 6001). Detalhes: {error_str[:200]}")
            elif '0x1788' in error_str or '6024' in error_str:
                raise Exception(f"Erro 0x1788 (6024): Slippage muito alto ou liquidez insuficiente. O preço mudou muito entre a cotação e a execução, ou não há liquidez suficiente para este swap. Tente aumentar o slippage ou vender em partes menores. Detalhes: {error_str[:300]}")
            else:
                raise Exception(f"Erro ao enviar transação: {error_str[:300]}")
    
    async def buy_token(self, token_address: str, amount_sol: float, max_slippage_bps: int = None) -> tuple:
        """Buy token with SOL
        Args:
            token_address: Token mint address to buy
            amount_sol: Amount in SOL (not lamports)
            max_slippage_bps: Slippage máximo em basis points (padrão: 1000 = 10%, pode aumentar até 2000 = 20%)
        Returns: (tx_signature, quote_data) where quote_data contains:
            - outAmount: quantidade de tokens recebidos (raw)
            - inAmount: quantidade de SOL enviada (lamports)
            - real_price: preço real calculado (SOL por token)
        """
        # SOL tem 9 decimais
        amount_sol_lamports = int(amount_sol * 1e9)
        
        try:
            # Tenta com slippage progressivo se não especificado
            slippage_levels = max_slippage_bps and [max_slippage_bps] or [1000, 1500, 2000]  # 10%, 15%, 20% (padrão: 10%)
            last_error = None
            
            for slippage_bps in slippage_levels:
                try:
                    print(f"   🔄 Tentando comprar com slippage: {slippage_bps/100}% ({slippage_bps} bps)")
                    
                    # Get quote: SOL -> Token com slippage específico
                    quote = await self.get_quote(SOL_MINT, token_address, amount_sol_lamports, slippage_bps=slippage_bps)
                    
                    if not quote.get('outAmount'):
                        raise Exception("Quote inválida: sem outAmount")
                    
                    # Calcula preço real a partir dos valores do swap
                    in_amount = int(quote.get('inAmount', amount_sol_lamports))
                    out_amount = int(quote.get('outAmount', 0))
            
                    # Preço real: quanto SOL custa cada token
                    # IMPORTANTE: Não calculamos preço aqui porque não sabemos os decimais do token
                    # O preço será calculado no bot.py usando o preço do Telegram (mais confiável)
                    # ou usando o saldo da carteira se disponível
                    
                    # Adiciona informações calculadas ao quote
                    quote['real_in_amount_sol'] = in_amount / 1e9
                    quote['real_out_amount_tokens'] = out_amount
                    # Preço será calculado no bot.py usando preço do Telegram
                    quote['calculated_price'] = 0  # Será substituído no bot.py
                    
                    # Execute swap (use_sol=True porque estamos usando SOL)
                    swap_transaction = await self.swap(quote, use_sol=True)
                    
                    # Obtém saldo ANTES da compra
                    balance_before = await self.get_wallet_sol_balance()
                    
                    # Send transaction
                    tx_signature = await self.send_transaction(swap_transaction)
                    
                    # Se chegou aqui, deu certo! Sai do loop
                    print(f"✅ Compra executada! TX: {tx_signature}")
                    print(f"   SOL gasto (quote): {quote['real_in_amount_sol']:.6f} SOL")
                    print(f"   Tokens recebidos (quote): {out_amount}")
                    print(f"   Preço calculado (quote): {quote['calculated_price']:.10f} SOL/token")
                    
                    # Obtém valores reais comparando saldo da carteira (método mais confiável)
                    print(f"   🔍 Consultando saldo da carteira para valores reais...")
                    balance_details = await self.get_transaction_details_by_balance(balance_before, wait_seconds=5)
                    
                    if balance_details and balance_details.get('confirmed'):
                        real_sol_spent = abs(balance_details['sol_received'])  # Deve ser negativo (gastou SOL), convertemos para positivo
                        
                        if real_sol_spent > 0:
                            # Tokens reais recebidos vêm do quote (outAmount é o que realmente foi recebido na transação)
                            real_tokens_received = out_amount
                            
                            # Calcula preço de entrada REAL: SOL_real_gasto / Tokens_reais_recebidos
                            # Preço = quanto SOL custa cada token
                            # outAmount está em unidades brutas do token (com decimais já aplicados)
                            # Para calcular o preço unitário correto:
                            # Preço = SOL gasto / (tokens recebidos / 10^decimais)
                            # Como não sabemos os decimais exatos, assumimos 9 decimais (padrão Solana)
                            # Mas o importante é manter a proporção correta
                            # Não calculamos preço aqui porque não sabemos os decimais do token
                            # O preço será usado do Telegram no bot.py (mais confiável)
                            quote['real_in_amount_sol'] = real_sol_spent
                            quote['real_out_amount_tokens'] = real_tokens_received
                            quote['from_balance'] = True
                            
                            print(f"   ✅ Valores reais calculados pelo saldo da carteira:")
                            print(f"      Saldo antes: {balance_before:.6f} SOL")
                            print(f"      Saldo depois: {balance_details['balance_after']:.6f} SOL")
                            print(f"      SOL gasto REAL: {real_sol_spent:.6f} SOL")
                            print(f"      Tokens recebidos REAL: {real_tokens_received}")
                            print(f"      Preço será usado do Telegram (mais confiável para tokens novos)")
                        else:
                            print(f"   ⚠️  Saldo não diminuiu como esperado, usando valores do quote")
                    else:
                        print(f"   ⚠️  Não foi possível calcular pelo saldo, usando valores do quote")
                    
                    # Tenta também obter detalhes da transação (método complementar)
                    try:
                        tx_details = await self.get_transaction_details(tx_signature, max_retries=2, wait_seconds=2)
                        if tx_details and tx_details.get('confirmed') and tx_details.get('tokens_sold', 0) > 0:
                            # Se conseguiu tokens da transação, usa para validar
                            if not quote.get('from_balance'):
                                quote['real_out_amount_tokens'] = tx_details['tokens_sold']
                                if tx_details.get('real_price', 0) > 0:
                                    quote['calculated_price'] = tx_details['real_price']
                                    quote['from_blockchain'] = True
                    except:
                        pass  # Não bloqueia se falhar
                    
                    return tx_signature, quote
                    
                except Exception as e:
                    error_str = str(e)
                    last_error = e
                    
                    # Verifica se é erro de slippage/liquidez (0x1771 = 6001 ou 0x1788 = 6024)
                    if '0x1771' in error_str or '6001' in error_str or '0x1788' in error_str or '6024' in error_str or 'slippage' in error_str.lower() or 'liquidez' in error_str.lower():
                        if slippage_bps < slippage_levels[-1]:  # Ainda tem níveis para tentar
                            print(f"   ⚠️  Erro de slippage/liquidez com {slippage_bps/100}% - tentando com slippage maior...")
                            continue
                        else:
                            # Último nível, tenta reduzir a quantidade
                            print(f"   ⚠️  Erro de slippage/liquidez mesmo com {slippage_bps/100}% - tentando com quantidade menor...")
                            
                            # Tenta comprar 50% da quantidade
                            half_amount = amount_sol / 2
                            if half_amount >= 0.001:  # Mínimo de 0.001 SOL
                                try:
                                    print(f"   🔄 Tentando comprar 50% primeiro ({half_amount} SOL)...")
                                    tx1, quote1 = await self.buy_token(token_address, half_amount, max_slippage_bps=2000)
                                    
                                    # Se deu certo, tenta comprar o resto
                                    remaining = amount_sol - half_amount
                                    if remaining >= 0.001:
                                        print(f"   🔄 Comprando os {remaining} SOL restantes...")
                                        tx2, quote2 = await self.buy_token(token_address, remaining, max_slippage_bps=2000)
                                        
                                        # Retorna a última transação e combina os quotes
                                        return tx2, {
                                            **quote2,
                                            'partial_buy': True,
                                            'first_tx': tx1,
                                            'second_tx': tx2,
                                            'total_tokens': quote1.get('real_out_amount_tokens', 0) + quote2.get('real_out_amount_tokens', 0),
                                            'total_sol_spent': quote1.get('real_in_amount_sol', 0) + quote2.get('real_in_amount_sol', 0)
                                        }
                                    else:
                                        return tx1, quote1
                                except Exception as partial_error:
                                    print(f"   ❌ Erro ao comprar em partes: {partial_error}")
                                    raise Exception(f"Erro de slippage/liquidez: Não foi possível comprar mesmo com quantidade reduzida. O token pode ter pouca liquidez. Detalhes: {error_str[:300]}")
                            else:
                                raise Exception(f"Erro de slippage/liquidez: Quantidade muito pequena para dividir. Detalhes: {error_str[:300]}")
                    else:
                        # Outro tipo de erro, propaga
                        raise
            
            # Se chegou aqui sem break, todas as tentativas falharam
            if last_error:
                raise last_error
            else:
                raise Exception("Erro desconhecido ao comprar token")
        except Exception as e:
            print(f"❌ Erro ao comprar token: {e}")
            raise
    
    async def sell_token(self, token_address: str, amount_tokens: int, max_slippage_bps: int = None, recursion_depth: int = 0, min_tokens_threshold: int = 1000000) -> tuple:
        """Sell token for SOL
        Args:
            token_address: Token mint address to sell
            amount_tokens: Amount in token's smallest unit (raw amount, not decimals)
            max_slippage_bps: Slippage máximo em basis points (padrão: 1000 = 10%, pode aumentar até 2000 = 20%)
            recursion_depth: Profundidade de recursão (para vendas em partes)
            min_tokens_threshold: Quantidade mínima de tokens para tentar vender
        Returns: (tx_signature, quote_data) where quote_data contains:
            - outAmount: quantidade de SOL recebida (lamports)
            - inAmount: quantidade de tokens vendidos (raw)
            - real_price: preço real de venda (SOL por token)
            - tokens_sold: quantidade real de tokens vendidos
            - tokens_requested: quantidade de tokens que tentou vender
            - partial_sale: True se foi venda parcial
            - remaining_tokens: quantidade de tokens que não conseguiu vender (se houver)
        """
        try:
            # Tenta com slippage progressivo se não especificado
            slippage_levels = max_slippage_bps and [max_slippage_bps] or [1000, 1500, 2000]  # 10%, 15%, 20% (padrão: 10%)
            last_error = None
            
            for slippage_bps in slippage_levels:
                try:
                    print(f"   🔄 Tentando vender com slippage: {slippage_bps/100}% ({slippage_bps} bps)")
                    
                    # Get quote: Token -> SOL com slippage específico
                    quote = await self.get_quote(token_address, SOL_MINT, amount_tokens, slippage_bps=slippage_bps)
                    
                    if not quote.get('outAmount'):
                        raise Exception("Quote inválida: sem outAmount")
                    
                    # Calcula valores reais do swap
                    in_amount = int(quote.get('inAmount', amount_tokens))
                    out_amount = int(quote.get('outAmount', 0))
                    
                    # Preço real de venda: quanto SOL recebe por token
                    real_price = (out_amount / 1e9) / (in_amount / 1e9) if in_amount > 0 else 0
                    
                    # Adiciona informações calculadas ao quote
                    quote['real_in_amount_tokens'] = in_amount
                    quote['real_out_amount_sol'] = out_amount / 1e9
                    quote['real_price'] = real_price
                    quote['calculated_price'] = (out_amount / 1e9) / in_amount if in_amount > 0 else 0
                    
                    # Execute swap (use_sol=True porque estamos vendendo para SOL)
                    swap_transaction = await self.swap(quote, use_sol=True)
                    
                    # Obtém saldo ANTES da venda
                    balance_before = await self.get_wallet_sol_balance()
                    
                    # Send transaction
                    tx_signature = await self.send_transaction(swap_transaction)
                    
                    # Se chegou aqui, deu certo! Sai do loop
                    print(f"✅ Venda executada! TX: {tx_signature}")
                    print(f"   Tokens vendidos (quote): {in_amount}")
                    print(f"   SOL recebido (quote): {quote['real_out_amount_sol']:.6f} SOL")
                    print(f"   Preço de venda (quote): {quote['calculated_price']:.10f} SOL/token")
                    
                    # Obtém valores reais comparando saldo da carteira (método mais confiável)
                    print(f"   🔍 Consultando saldo da carteira para valores reais...")
                    balance_details = await self.get_transaction_details_by_balance(balance_before, wait_seconds=5)
                    
                    if balance_details and balance_details.get('confirmed'):
                        real_sol_received = balance_details['sol_received']  # Deve ser positivo (recebeu SOL)
                        
                        # Verifica se realmente recebeu SOL (pode ser negativo se ainda não confirmou)
                        if real_sol_received > 0.0001:  # Mínimo de 0.0001 SOL para considerar válido
                            quote['real_out_amount_sol'] = real_sol_received
                            quote['real_in_amount_tokens'] = in_amount
                            quote['from_balance'] = True
                            
                            print(f"   ✅ Valores reais calculados pelo saldo da carteira:")
                            print(f"      Saldo antes: {balance_before:.6f} SOL")
                            print(f"      Saldo depois: {balance_details['balance_after']:.6f} SOL")
                            print(f"      SOL recebido REAL: {real_sol_received:.6f} SOL")
                            print(f"      Tokens vendidos: {in_amount}")
                        elif real_sol_received <= 0:
                            print(f"   ⚠️  Saldo não aumentou ainda (mudança: {real_sol_received:.6f} SOL) - transação pode estar pendente")
                            print(f"   💡 Usando valores do quote: {quote.get('real_out_amount_sol', 0):.6f} SOL")
                        else:
                            print(f"   ⚠️  Mudança muito pequena ({real_sol_received:.6f} SOL) - usando valores do quote")
                    else:
                        print(f"   ⚠️  Não foi possível calcular pelo saldo, usando valores do quote")
                    
                    # Tenta também obter detalhes da transação (método complementar)
                    try:
                        tx_details = await self.get_transaction_details(tx_signature, max_retries=2, wait_seconds=2)
                        if tx_details and tx_details.get('confirmed') and tx_details.get('tokens_sold', 0) > 0:
                            # Se conseguiu tokens da transação, usa para validar
                            if not quote.get('from_balance'):
                                quote['real_in_amount_tokens'] = tx_details['tokens_sold']
                                if tx_details.get('real_price', 0) > 0:
                                    quote['calculated_price'] = tx_details['real_price']
                                    quote['from_blockchain'] = True
                    except:
                        pass  # Não bloqueia se falhar
                    
                    # Adiciona informações sobre quantidade vendida
                    quote['tokens_requested'] = amount_tokens
                    quote['tokens_sold'] = in_amount
                    quote['remaining_tokens'] = amount_tokens - in_amount
                    quote['partial_sale'] = quote['remaining_tokens'] > 0
                    
                    return tx_signature, quote
                    
                except Exception as e:
                    error_str = str(e)
                    last_error = e
                    
                    # Verifica se é erro de slippage/liquidez (0x1788 = 6024)
                    if '0x1788' in error_str or '6024' in error_str or 'custom program error' in error_str:
                        if slippage_bps < slippage_levels[-1]:  # Ainda tem níveis para tentar
                            print(f"   ⚠️  Erro 0x1788 (slippage/liquidez) com {slippage_bps/100}% - tentando com slippage maior...")
                            continue
                        else:
                            # Último nível, tenta dividir a venda
                            print(f"   ⚠️  Erro 0x1788 mesmo com {slippage_bps/100}% - tentando vender em partes menores...")
                            
                            # Limita profundidade de recursão (máximo 3 divisões para evitar loops infinitos)
                            if recursion_depth >= 3:
                                # Retorna erro especial indicando venda parcial
                                raise Exception(f"LIQUIDITY_INSUFFICIENT: Não foi possível vender {amount_tokens} tokens. Liquidez insuficiente mesmo após múltiplas tentativas. Detalhes: {error_str[:200]}")
                            
                            # Limita quantidade mínima (se for muito pequeno, não vale a pena)
                            if amount_tokens < min_tokens_threshold:
                                raise Exception(f"LIQUIDITY_INSUFFICIENT: Quantidade muito pequena ({amount_tokens} tokens) para vender. Detalhes: {error_str[:200]}")
                            
                            # Tenta vender 50% primeiro
                            half_amount = amount_tokens // 2
                            if half_amount > 0 and half_amount >= min_tokens_threshold:
                                try:
                                    print(f"   🔄 Tentando vender 50% primeiro ({half_amount} tokens)...")
                                    tx1, quote1 = await self.sell_token(token_address, half_amount, max_slippage_bps=2000, recursion_depth=recursion_depth+1, min_tokens_threshold=min_tokens_threshold)
                                    
                                    # Calcula tokens realmente vendidos na primeira parte
                                    tokens_sold_1 = quote1.get('real_in_amount_tokens', quote1.get('inAmount', half_amount))
                                    
                                    # Se deu certo, tenta vender o resto
                                    remaining = amount_tokens - tokens_sold_1
                                    if remaining > 0 and remaining >= min_tokens_threshold:
                                        print(f"   🔄 Vendendo os {remaining} tokens restantes...")
                                        try:
                                            tx2, quote2 = await self.sell_token(token_address, remaining, max_slippage_bps=2000, recursion_depth=recursion_depth+1, min_tokens_threshold=min_tokens_threshold)
                                            
                                            # Calcula tokens realmente vendidos na segunda parte
                                            tokens_sold_2 = quote2.get('real_in_amount_tokens', quote2.get('inAmount', remaining))
                                            total_sold = tokens_sold_1 + tokens_sold_2
                                            remaining_unsold = amount_tokens - total_sold
                                            
                                            # Retorna a última transação e combina os quotes
                                            return tx2, {
                                                **quote2,
                                                'partial_sale': remaining_unsold > 0,
                                                'tokens_requested': amount_tokens,
                                                'tokens_sold': total_sold,
                                                'remaining_tokens': remaining_unsold,
                                                'first_tx': tx1,
                                                'second_tx': tx2,
                                                'real_out_amount_sol': quote1.get('real_out_amount_sol', 0) + quote2.get('real_out_amount_sol', 0)
                                            }
                                        except Exception as second_error:
                                            # Se a segunda parte falhou, retorna apenas a primeira
                                            print(f"   ⚠️  Não foi possível vender o restante: {second_error}")
                                            remaining_unsold = remaining
                                            return tx1, {
                                                **quote1,
                                                'partial_sale': True,
                                                'tokens_requested': amount_tokens,
                                                'tokens_sold': tokens_sold_1,
                                                'remaining_tokens': remaining_unsold,
                                                'first_tx': tx1,
                                                'second_tx': None,
                                                'second_sale_failed': True
                                            }
                                    else:
                                        # Se o restante é muito pequeno, retorna apenas a primeira parte
                                        remaining_unsold = remaining
                                        return tx1, {
                                            **quote1,
                                            'partial_sale': remaining_unsold > 0,
                                            'tokens_requested': amount_tokens,
                                            'tokens_sold': tokens_sold_1,
                                            'remaining_tokens': remaining_unsold
                                        }
                                except Exception as partial_error:
                                    error_msg = str(partial_error)
                                    # Se for erro de liquidez insuficiente, propaga com informações
                                    if 'LIQUIDITY_INSUFFICIENT' in error_msg:
                                        raise Exception(f"LIQUIDITY_INSUFFICIENT: Não foi possível vender {amount_tokens} tokens. {error_msg}")
                                    print(f"   ❌ Erro ao vender em partes: {partial_error}")
                                    raise Exception(f"Erro 0x1788: Slippage muito alto ou liquidez insuficiente. Tente vender manualmente ou aguarde mais liquidez. Detalhes: {error_str[:300]}")
                            else:
                                raise Exception(f"LIQUIDITY_INSUFFICIENT: Quantidade muito pequena ({amount_tokens} tokens) para dividir. Detalhes: {error_str[:200]}")
                    else:
                        # Outro tipo de erro, propaga
                        raise
            
            # Se chegou aqui sem break, todas as tentativas falharam
            if last_error:
                raise last_error
            else:
                raise Exception("Erro desconhecido ao vender token")
            
            # Tenta também obter detalhes da transação (método complementar)
            try:
                tx_details = await self.get_transaction_details(tx_signature, max_retries=2, wait_seconds=2)
                if tx_details and tx_details.get('confirmed') and tx_details.get('tokens_sold', 0) > 0:
                    # Se conseguiu tokens da transação, usa para validar
                    if not quote.get('from_balance'):
                        quote['real_in_amount_tokens'] = tx_details['tokens_sold']
                        if tx_details.get('real_price', 0) > 0:
                            quote['calculated_price'] = tx_details['real_price']
                            quote['from_blockchain'] = True
            except:
                pass  # Não bloqueia se falhar
            
            return tx_signature, quote
        except Exception as e:
            print(f"❌ Erro ao vender token: {e}")
            raise
    
    async def get_wallet_sol_balance(self) -> float:
        """Obtém saldo atual de SOL da carteira"""
        try:
            balance = await self.client.get_balance(self.keypair.pubkey())
            return balance.value / 1e9  # Converte lamports para SOL
        except Exception as e:
            print(f"⚠️  Erro ao obter saldo: {e}")
            return 0.0
    
    async def get_transaction_details_by_balance(self, balance_before: float, wait_seconds: int = 5) -> Optional[Dict]:
        """Obtém valores reais da transação comparando saldo antes/depois
        Args:
            balance_before: Saldo de SOL antes da transação
            wait_seconds: Segundos para aguardar confirmação (padrão: 5 segundos)
        Returns:
            Dict com valores reais: {
                'sol_received': float,  # Positivo para venda, negativo para compra
                'sol_change': float,    # Mudança no saldo
                'confirmed': bool
            }
        """
        # Aguarda confirmação (aumentado para 5 segundos para dar tempo da transação confirmar)
        await asyncio.sleep(wait_seconds)
        
        # Obtém saldo após transação
        balance_after = await self.get_wallet_sol_balance()
        
        # Calcula diferença
        sol_change = balance_after - balance_before
        
        return {
            'sol_received': sol_change,  # Positivo = recebeu SOL (venda), Negativo = gastou SOL (compra)
            'sol_change': sol_change,
            'balance_before': balance_before,
            'balance_after': balance_after,
            'confirmed': True
        }
    
    async def get_transaction_details(self, tx_signature: str, max_retries: int = 5, wait_seconds: int = 3) -> Optional[Dict]:
        """Obtém detalhes reais da transação do Solscan/RPC após confirmação
        Args:
            tx_signature: Assinatura da transação
            max_retries: Número máximo de tentativas
            wait_seconds: Segundos para aguardar confirmação
        Returns:
            Dict com valores reais: {
                'sol_received': float,
                'tokens_sold': int,
                'real_price': float,
                'confirmed': bool
            }
        """
        # Aguarda confirmação
        await asyncio.sleep(wait_seconds)
        
        for attempt in range(max_retries):
            try:
                # Converte string para Signature se necessário
                # O AsyncClient pode aceitar string diretamente em algumas versões
                try:
                    from solders.signature import Signature
                    if isinstance(tx_signature, str):
                        # Tenta converter de base58
                        sig_bytes = b58decode(tx_signature)
                        sig = Signature.from_bytes(sig_bytes)
                    else:
                        sig = tx_signature
                except Exception as conv_error:
                    # Se falhar na conversão, tenta usar string diretamente
                    # Alguns clientes aceitam string
                    sig = tx_signature
                
                # Tenta obter via RPC da Solana
                # Se ainda der erro, tenta com string diretamente
                try:
                    result = await self.client.get_transaction(
                        sig,
                        encoding="jsonParsed",
                        max_supported_transaction_version=0
                    )
                except TypeError:
                    # Se o cliente não aceitar o tipo, tenta com string
                    result = await self.client.get_transaction(
                        tx_signature,
                        encoding="jsonParsed",
                        max_supported_transaction_version=0
                    )
                
                if result.value is None:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    return None
                
                transaction = result.value
                meta = transaction.transaction.meta if hasattr(transaction, 'transaction') and transaction.transaction else None
                
                if not meta:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    return None
                
                sol_received = 0.0
                tokens_sold = 0
                token_mint = None
                
                # Analisa token balances (pre e post)
                pre_token_balances = getattr(meta, 'pre_token_balances', None) or []
                post_token_balances = getattr(meta, 'post_token_balances', None) or []
                
                # Calcula diferença de tokens
                pre_balances_dict = {}
                for bal in pre_token_balances:
                    account_idx = getattr(bal, 'account_index', None)
                    if account_idx is not None:
                        ui_amount = getattr(getattr(bal, 'ui_token_amount', None), 'ui_amount', 0) or 0
                        mint = getattr(bal, 'mint', None)
                        pre_balances_dict[account_idx] = {'amount': ui_amount, 'mint': mint}
                
                post_balances_dict = {}
                for bal in post_token_balances:
                    account_idx = getattr(bal, 'account_index', None)
                    if account_idx is not None:
                        ui_amount = getattr(getattr(bal, 'ui_token_amount', None), 'ui_amount', 0) or 0
                        mint = getattr(bal, 'mint', None)
                        post_balances_dict[account_idx] = {'amount': ui_amount, 'mint': mint}
                        
                        # Verifica se tokens foram vendidos (saldo diminuiu)
                        if account_idx in pre_balances_dict:
                            pre_amount = pre_balances_dict[account_idx]['amount']
                            post_amount = ui_amount
                            if pre_amount > post_amount:
                                diff = pre_amount - post_amount
                                tokens_sold = int(diff * 1e9)  # Converte para raw (assume 9 decimais)
                                token_mint = str(mint) if mint else None
                
                # Calcula SOL recebido (diferença de saldo SOL)
                pre_balances = getattr(meta, 'pre_balances', None) or []
                post_balances = getattr(meta, 'post_balances', None) or []
                
                if pre_balances and post_balances and len(pre_balances) > 0 and len(post_balances) > 0:
                    # Pega o primeiro account (geralmente é a carteira principal)
                    pre_sol = pre_balances[0] / 1e9 if pre_balances[0] else 0
                    post_sol = post_balances[0] / 1e9 if post_balances[0] else 0
                    sol_received = post_sol - pre_sol
                
                # Se não conseguiu valores, tenta via Solscan API pública
                if (sol_received == 0 and tokens_sold == 0) or attempt == max_retries - 1:
                    try:
                        async with aiohttp.ClientSession() as session:
                            # API pública do Solscan (sem autenticação)
                            url = f"https://public-api.solscan.io/transaction/{tx_signature}"
                            headers = {
                                "User-Agent": "Mozilla/5.0",
                                "Accept": "application/json"
                            }
                            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    # Solscan retorna estrutura diferente, tenta extrair
                                    # Nota: estrutura pode variar, então usamos como fallback
                                    pass
                    except Exception as e:
                        pass
                
                # Calcula preço real se temos ambos os valores
                real_price = 0.0
                if tokens_sold > 0 and sol_received > 0:
                    # Converte tokens para unidades (assume 9 decimais)
                    tokens_in_units = tokens_sold / 1e9
                    real_price = sol_received / tokens_in_units if tokens_in_units > 0 else 0
                
                # Retorna mesmo se não conseguiu todos os valores (pode ser útil)
                return {
                    'sol_received': sol_received,
                    'tokens_sold': tokens_sold,
                    'real_price': real_price,
                    'token_mint': token_mint,
                    'confirmed': True
                }
                
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                print(f"⚠️  Erro ao obter detalhes da transação {tx_signature[:8]}...: {e}")
                return None
        
        return None
    
    async def close(self):
        """Close RPC client"""
        await self.client.close()

