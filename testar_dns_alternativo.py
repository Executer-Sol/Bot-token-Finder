"""
Testa se api.jup.ag resolve DNS (alternativa ao quote-api.jup.ag)
"""
import socket
import aiohttp
import asyncio

async def testar_dns():
    """Testa resolução DNS de diferentes endpoints Jupiter"""
    print("="*70)
    print("TESTE: Resolução DNS de Endpoints Jupiter")
    print("="*70)
    print()
    
    endpoints = [
        "quote-api.jup.ag",
        "api.jup.ag",
        "price.jup.ag",
        "jup.ag"
    ]
    
    for endpoint in endpoints:
        print(f"Testando: {endpoint}")
        try:
            ip = socket.gethostbyname(endpoint)
            print(f"  ✅ DNS OK: {ip}")
        except socket.gaierror as e:
            print(f"  ❌ DNS FALHOU: {e}")
        print()
    
    print("-"*70)
    print("Testando conexão HTTP...")
    print()
    
    # Testa conexão HTTP
    test_urls = [
        "https://api.jup.ag/price/v3?ids=So11111111111111111111111111111111111111112",
        "https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=1000000000&slippageBps=50"
    ]
    
    for url in test_urls:
        print(f"Testando: {url[:60]}...")
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"  ✅ HTTP OK: Status {response.status}")
                    else:
                        print(f"  ⚠️  HTTP: Status {response.status}")
        except aiohttp.ClientConnectorError as e:
            print(f"  ❌ CONEXÃO FALHOU: {e}")
        except Exception as e:
            print(f"  ❌ ERRO: {e}")
        print()

if __name__ == "__main__":
    asyncio.run(testar_dns())











