"""
Integração com Alchemy Data APIs para melhorar coleta de informações
"""
import asyncio
import aiohttp
import os
from typing import Dict, List, Optional
from datetime import datetime

class AlchemyClient:
    def __init__(self, api_key: str = None):
        # Tenta buscar API key na seguinte ordem:
        # 1. Parâmetro fornecido
        # 2. Variável de ambiente ALCHEMY_API_KEY
        # 3. Extrai do RPC_URL se for Alchemy
        self.api_key = api_key or os.getenv('ALCHEMY_API_KEY')
        
        # Se não tiver, tenta extrair do RPC_URL
        if not self.api_key:
            rpc_url = os.getenv('RPC_URL', '')
            if 'alchemy.com' in rpc_url and '/v2/' in rpc_url:
                # Extrai API key do RPC URL: https://solana-mainnet.g.alchemy.com/v2/API_KEY
                parts = rpc_url.split('/v2/')
                if len(parts) > 1:
                    self.api_key = parts[1].strip()
        
        self.base_url = "https://solana-mainnet.g.alchemy.com/v0"
        self.rpc_url = f"https://solana-mainnet.g.alchemy.com/v2/{self.api_key}" if self.api_key else None
    
    def is_configured(self) -> bool:
        """Verifica se API key está configurada"""
        return self.api_key is not None and len(self.api_key) > 0
    
    async def get_portfolio(self, wallet_address: str) -> Optional[Dict]:
        """Busca portfólio completo via Portfolio API
        
        Retorna:
        {
            'sol_balance': float,
            'tokens': [
                {
                    'mint': str,
                    'symbol': str,
                    'balance': float,
                    'value_usd': float,
                    'price_usd': float
                }
            ],
            'total_value_usd': float
        }
        """
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/accounts/{wallet_address}/portfolio"
            headers = {"X-Alchemy-Token": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_portfolio(data)
                    else:
                        print(f"⚠️  Erro ao buscar portfolio Alchemy: {response.status}")
                        return None
        except Exception as e:
            print(f"⚠️  Erro ao buscar portfolio Alchemy: {e}")
            return None
    
    def _parse_portfolio(self, data: Dict) -> Dict:
        """Parse da resposta do Portfolio API"""
        try:
            portfolio = {
                'sol_balance': 0.0,
                'tokens': [],
                'total_value_usd': 0.0
            }
            
            # Parse SOL balance
            if 'sol_balance' in data:
                portfolio['sol_balance'] = float(data['sol_balance'])
            
            # Parse tokens
            if 'tokens' in data:
                for token in data['tokens']:
                    portfolio['tokens'].append({
                        'mint': token.get('mint', ''),
                        'symbol': token.get('symbol', 'UNKNOWN'),
                        'balance': float(token.get('balance', 0)),
                        'value_usd': float(token.get('value_usd', 0)),
                        'price_usd': float(token.get('price_usd', 0))
                    })
            
            # Total value
            if 'total_value_usd' in data:
                portfolio['total_value_usd'] = float(data['total_value_usd'])
            
            return portfolio
        except Exception as e:
            print(f"⚠️  Erro ao parsear portfolio: {e}")
            return None
    
    async def get_transfers(self, wallet_address: str, limit: int = 100, 
                           category: str = None, from_block: int = None) -> Optional[List[Dict]]:
        """Busca transferências via Transfers API
        
        Args:
            wallet_address: Endereço da carteira
            limit: Número máximo de transferências
            category: 'external', 'internal', 'erc20', etc.
            from_block: Bloco inicial (opcional)
        
        Retorna lista de transferências:
        [
            {
                'hash': str,
                'from': str,
                'to': str,
                'value': float,
                'token_address': str,
                'token_symbol': str,
                'category': str,
                'block_timestamp': str,
                'block_number': int
            }
        ]
        """
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/accounts/{wallet_address}/transfers"
            headers = {"X-Alchemy-Token": self.api_key}
            params = {"limit": limit}
            
            if category:
                params['category'] = category
            if from_block:
                params['fromBlock'] = from_block
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, 
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_transfers(data)
                    else:
                        print(f"⚠️  Erro ao buscar transfers Alchemy: {response.status}")
                        return None
        except Exception as e:
            print(f"⚠️  Erro ao buscar transfers Alchemy: {e}")
            return None
    
    def _parse_transfers(self, data: Dict) -> List[Dict]:
        """Parse da resposta do Transfers API"""
        try:
            transfers = []
            if 'transfers' in data:
                for tx in data['transfers']:
                    transfers.append({
                        'hash': tx.get('hash', ''),
                        'from': tx.get('from', ''),
                        'to': tx.get('to', ''),
                        'value': float(tx.get('value', 0)),
                        'token_address': tx.get('token_address', ''),
                        'token_symbol': tx.get('token_symbol', 'UNKNOWN'),
                        'category': tx.get('category', 'external'),
                        'block_timestamp': tx.get('block_timestamp', ''),
                        'block_number': tx.get('block_number', 0)
                    })
            return transfers
        except Exception as e:
            print(f"⚠️  Erro ao parsear transfers: {e}")
            return []
    
    async def get_token_price(self, token_address: str) -> Optional[float]:
        """Busca preço de um token via Prices API
        
        Retorna preço em USD ou None se não encontrado
        """
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/prices/token/{token_address}"
            headers = {"X-Alchemy-Token": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('price', 0))
                    else:
                        return None
        except Exception as e:
            print(f"⚠️  Erro ao buscar preço Alchemy: {e}")
            return None
    
    async def detect_sells(self, wallet_address: str, limit: int = 100) -> List[Dict]:
        """Detecta vendas automaticamente via Transfers API
        
        Identifica transferências onde a carteira recebeu SOL (vendas)
        """
        transfers = await self.get_transfers(wallet_address, limit=limit)
        if not transfers:
            return []
        
        # Filtra apenas transferências que receberam SOL (vendas)
        sells = []
        for transfer in transfers:
            # Se recebeu SOL (to == wallet e value > 0)
            if (transfer['to'].upper() == wallet_address.upper() and 
                transfer['value'] > 0 and
                transfer['category'] == 'external'):
                sells.append({
                    'signature': transfer['hash'],
                    'timestamp': transfer['block_timestamp'],
                    'sol_received': transfer['value'],
                    'token_mint': transfer['token_address'],
                    'token_symbol': transfer['token_symbol'],
                    'block_number': transfer['block_number']
                })
        
        return sells
    
    async def get_wallet_tokens_with_prices(self, wallet_address: str) -> List[Dict]:
        """Busca todos os tokens da carteira com preços via Portfolio API"""
        portfolio = await self.get_portfolio(wallet_address)
        if not portfolio:
            return []
        
        return portfolio.get('tokens', [])

def get_alchemy_client() -> AlchemyClient:
    """Retorna instância do cliente Alchemy"""
    return AlchemyClient()

async def update_sell_prices_with_alchemy(wallet_address: str, api_key: str = None) -> int:
    """Atualiza preços de venda usando Alchemy Transfers API
    
    Args:
        wallet_address: Endereço da carteira
        api_key: API key do Alchemy (opcional, tenta buscar automaticamente)
    
    Retorna número de preços atualizados
    """
    client = AlchemyClient(api_key) if api_key else get_alchemy_client()
    if not client.is_configured():
        print("⚠️  Alchemy API key não configurada")
        return 0
    
    # Detecta vendas
    sells = await client.detect_sells(wallet_address, limit=100)
    
    if not sells:
        print("ℹ️  Nenhuma venda detectada via Alchemy")
        return 0
    
    # Carrega trades vendidos
    import json
    trades_file = 'trades_history.json'
    if not os.path.exists(trades_file):
        return 0
    
    with open(trades_file, 'r', encoding='utf-8') as f:
        trades_data = json.load(f)
    
    sold_trades = trades_data.get('sold', [])
    updated_count = 0
    
    # Obtém preço do SOL
    sol_price = await client.get_token_price("So11111111111111111111111111111111111111112") or 150.0
    
    # Atualiza preços
    for trade in sold_trades:
        contract_address = trade.get('contract_address', '').upper()
        
        # Procura venda correspondente
        matching_sell = None
        for sell in sells:
            if sell['token_mint'].upper() == contract_address:
                matching_sell = sell
                break
        
        if matching_sell:
            # Calcula preço de venda em USD
            # Se temos sol_received, podemos calcular se tivermos quantidade de tokens
            amount_tokens = trade.get('amount_tokens', 0)
            if amount_tokens > 0:
                price_per_token_sol = matching_sell['sol_received'] / amount_tokens
                price_per_token_usd = price_per_token_sol * sol_price
                
                trade['final_price'] = price_per_token_usd
                trade['real_sell_price_calculated'] = True
                trade['real_sol_received'] = matching_sell['sol_received']
                trade['sell_tx_signature'] = matching_sell['signature']
                
                updated_count += 1
                print(f"✅ Atualizado {trade.get('symbol', 'UNKNOWN')}: ${price_per_token_usd:.10f}")
    
    # Salva atualizações
    if updated_count > 0:
        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ {updated_count} preços atualizados via Alchemy!")
    
    return updated_count

def update_sell_prices_with_alchemy_sync(wallet_address: str, api_key: str = None) -> int:
    """Wrapper síncrono"""
    return asyncio.run(update_sell_prices_with_alchemy(wallet_address, api_key))

