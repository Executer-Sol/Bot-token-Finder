"""
Monitor de preços de tokens - busca preço de múltiplas fontes
"""
import aiohttp
import config

class PriceMonitor:
    def __init__(self):
        self.birdeye_api_key = config.BIRDEYE_API_KEY if hasattr(config, 'BIRDEYE_API_KEY') else ''
    
    async def get_token_price_birdeye(self, token_address: str) -> float:
        """Busca preço usando BirdEye API"""
        if not self.birdeye_api_key:
            return None
        
        try:
            url = f"https://public-api.birdeye.so/v1/token/price?address={token_address}"
            headers = {"X-API-KEY": self.birdeye_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('data', {}).get('value', 0))
        except:
            return None
    
    async def get_token_price_jupiter(self, token_address: str) -> float:
        """Busca preço usando Jupiter Price API"""
        try:
            url = f"https://price.jup.ag/v4/price?ids={token_address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        price_data = data.get('data', {}).get(token_address, {})
                        return float(price_data.get('price', 0))
        except:
            return None
    
    async def get_token_price_dexscreener(self, token_address: str) -> float:
        """Busca preço usando DexScreener API"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        pairs = data.get('pairs', [])
                        if pairs and len(pairs) > 0:
                            # Pega o preço do primeiro par (geralmente o mais líquido)
                            price = float(pairs[0].get('priceUsd', 0))
                            return price
        except:
            return None
    
    async def get_token_price_alchemy(self, token_address: str) -> float:
        """Busca preço usando Alchemy API (se disponível)"""
        try:
            # Alchemy não tem API de preços direta, mas podemos usar Jupiter via Alchemy RPC
            # Por enquanto, retorna None - Alchemy RPC é usada para transações, não preços
            # Preços são obtidos via APIs especializadas (BirdEye, Jupiter, DexScreener)
            return None
        except:
            return None
    
    async def get_token_price(self, token_address: str) -> float:
        """
        Busca preço do token usando múltiplas fontes com fallback
        Ordem: BirdEye > Jupiter > DexScreener
        
        NOTA: A RPC da Alchemy (https://solana-mainnet.g.alchemy.com/v2/...) 
        é usada para TRANSAÇÕES na blockchain, não para preços em USD.
        Para preços em tempo real, usamos APIs especializadas:
        - BirdEye: Mais preciso, requer API key
        - Jupiter: Gratuita, boa cobertura
        - DexScreener: Gratuita, fallback
        """
        # Tenta BirdEye primeiro (se tiver API key)
        if self.birdeye_api_key:
            price = await self.get_token_price_birdeye(token_address)
            if price and price > 0:
                return price
        
        # Tenta Jupiter (gratuita, boa cobertura)
        price = await self.get_token_price_jupiter(token_address)
        if price and price > 0:
            return price
        
        # Tenta DexScreener (fallback)
        price = await self.get_token_price_dexscreener(token_address)
        if price and price > 0:
            return price
        
        return None








