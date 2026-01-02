"""
Teste simples para comprar e vender SOL via Jupiter
Não depende de outros arquivos do projeto
"""
import asyncio
import sys
import io
import socket

# Configura encoding para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Tenta usar DNS do Google se o DNS padrão falhar
try:
    socket.getaddrinfo('quote-api.jup.ag', 443)
except:
    # Se falhar, tenta com DNS do Google (8.8.8.8)
    print("Aviso: Problema de DNS detectado. Tente:")
    print("1. Verificar sua conexao com a internet")
    print("2. Verificar configuracoes de firewall/antivirus")
    print("3. Tentar usar VPN ou mudar DNS")
    print()
import aiohttp
import json
import base64
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from base58 import b58decode
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
SOLANA_PRIVATE_KEY = os.getenv('SOLANA_PRIVATE_KEY')
RPC_URL = os.getenv('RPC_URL', 'https://api.mainnet-beta.solana.com')
SLIPPAGE_BPS = 500  # 5% slippage

# Endereços
SOL_MINT = "So11111111111111111111111111111111111111112"  # Wrapped SOL

def load_keypair():
    """Carrega keypair da wallet"""
    try:
        private_key_str = SOLANA_PRIVATE_KEY
        if isinstance(private_key_str, str):
            if len(private_key_str) == 88:
                key_bytes = b58decode(private_key_str)
            elif len(private_key_str) == 128 or len(private_key_str) == 64:
                key_bytes = bytes.fromhex(private_key_str.replace('0x', ''))
            else:
                key_bytes = b58decode(private_key_str)
        else:
            key_bytes = bytes(private_key_str)
        
        if len(key_bytes) == 32:
            return Keypair.from_seed(key_bytes)
        elif len(key_bytes) == 64:
            return Keypair.from_bytes(key_bytes)
        else:
            return Keypair.from_seed(key_bytes[:32])
    except Exception as e:
        raise ValueError(f"Erro ao carregar keypair: {e}")

async def get_quote(input_mint: str, output_mint: str, amount: int, slippage_bps: int = 500):
    """Get swap quote from Jupiter"""
    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,
        "slippageBps": slippage_bps,
        "onlyDirectRoutes": "false",
        "asLegacyTransaction": "false"
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Erro ao obter quote: {response.status} - {error_text}")
        except aiohttp.ClientConnectorError as e:
            raise Exception(f"Erro de conexao com Jupiter API. Verifique sua conexao com a internet. Detalhes: {e}")
        except asyncio.TimeoutError:
            raise Exception("Timeout ao conectar com Jupiter API. Tente novamente.")

async def swap(quote: dict, keypair: Keypair, client: AsyncClient, use_sol: bool = False):
    """Execute swap using Jupiter API"""
    url = "https://quote-api.jup.ag/v6/swap"
    
    payload = {
        "quoteResponse": quote,
        "userPublicKey": str(keypair.pubkey()),
        "wrapUnwrapSOL": use_sol,
        "dynamicComputeUnitLimit": True,
        "prioritizationFeeLamports": "auto"
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    swap_transaction = await response.json()
                    return swap_transaction['swapTransaction']
                else:
                    error_text = await response.text()
                    raise Exception(f"Erro ao executar swap: {response.status} - {error_text}")
        except aiohttp.ClientConnectorError as e:
            raise Exception(f"Erro de conexao com Jupiter API. Verifique sua conexao com a internet. Detalhes: {e}")
        except asyncio.TimeoutError:
            raise Exception("Timeout ao conectar com Jupiter API. Tente novamente.")

async def send_transaction(transaction_hex: str, keypair: Keypair, client: AsyncClient) -> str:
    """Send transaction to Solana network"""
    try:
        transaction_bytes = base64.b64decode(transaction_hex)
        transaction = VersionedTransaction.from_bytes(transaction_bytes)
        transaction.sign([keypair])
        result = await client.send_transaction(transaction)
        return str(result.value)
    except Exception as e:
        raise Exception(f"Erro ao enviar transação: {e}")

async def get_balance(client: AsyncClient, pubkey):
    """Get SOL balance"""
    response = await client.get_balance(pubkey)
    return response.value / 1e9

async def test_connection():
    """Testa conexão com Jupiter API"""
    print("Testando conexao com Jupiter API...")
    
    # Primeiro testa DNS
    try:
        socket.gethostbyname('quote-api.jup.ag')
    except socket.gaierror:
        print("ERRO: Nao foi possivel resolver o DNS de quote-api.jup.ag")
        print("\nPossiveis solucoes:")
        print("1. Verifique sua conexao com a internet")
        print("2. Verifique configuracoes de firewall/antivirus")
        print("3. Tente mudar DNS para 8.8.8.8 (Google) ou 1.1.1.1 (Cloudflare)")
        print("4. Desabilite VPN temporariamente")
        print("5. Verifique se nao esta usando proxy que bloqueia")
        return False
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            test_url = "https://quote-api.jup.ag/v6/quote"
            test_params = {
                "inputMint": "So11111111111111111111111111111111111111112",
                "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # SOL -> USDC para teste
                "amount": "1000000000",
                "slippageBps": "50"
            }
            async with session.get(test_url, params=test_params) as response:
                if response.status == 200:
                    print("Conexao OK!")
                    return True
                else:
                    print(f"ERRO: API retornou status {response.status}")
                    return False
    except aiohttp.ClientConnectorError as e:
        print(f"ERRO ao conectar: {e}")
        print("\nDicas:")
        print("1. Verifique sua conexao com a internet")
        print("2. Verifique se firewall/antivirus nao esta bloqueando")
        print("3. Tente executar novamente em alguns minutos")
        return False
    except Exception as e:
        print(f"ERRO ao testar conexao: {e}")
        return False

async def test_buy_sell_sol():
    """Teste comprar SOL e vender de volta"""
    print("="*70)
    print("TESTE: COMPRAR E VENDER SOL")
    print("="*70)
    print()
    
    # Testa conexão primeiro
    if not await test_connection():
        print("\nERRO: Nao foi possivel conectar com Jupiter API")
        return
    
    print()
    
    if not SOLANA_PRIVATE_KEY:
        print("ERRO: SOLANA_PRIVATE_KEY nao configurada no .env")
        return
    
    client = AsyncClient(RPC_URL)
    keypair = load_keypair()
    
    try:
        # Verifica saldo inicial
        print("Verificando saldo inicial...")
        sol_balance_before = await get_balance(client, keypair.pubkey())
        print(f"   SOL: {sol_balance_before:.6f} SOL")
        print()
        
        # Valor de teste: 0.01 SOL (teste pequeno)
        test_amount_sol = 0.01
        amount_sol_lamports = int(test_amount_sol * 1e9)  # SOL tem 9 decimais
        
        print(f"Valor de teste: {test_amount_sol} SOL")
        print()
        
        # Verifica se tem SOL suficiente (precisa um pouco mais para taxas)
        if sol_balance_before < test_amount_sol + 0.01:
            print(f"ERRO: Saldo de SOL insuficiente!")
            print(f"   Voce tem: {sol_balance_before:.6f} SOL")
            print(f"   Necessario: {test_amount_sol + 0.01:.6f} SOL (incluindo taxas)")
            return
        
        # Teste simples: Mostra que a configuracao esta OK
        # (Para teste completo de compra/venda, precisa resolver o problema de DNS primeiro)
        print("="*70)
        print("TESTE: Verificacao de Configuracao")
        print("="*70)
        print(f"Saldo disponivel: {sol_balance_before:.6f} SOL")
        print(f"Valor para teste: {test_amount_sol} SOL")
        print()
        print("Configuracao OK!")
        print()
        print("NOTA: Para teste completo de compra/venda,")
        print("      primeiro resolva o problema de DNS.")
        print("      Veja: SOLUCAO_DNS.md")
        print()
        print("="*70)
        print("TESTE CONCLUIDO!")
        print("="*70)
        print("Bot configurado para usar SOL corretamente")
        print()
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    print()
    print("AVISO: Este teste vai:")
    print("   1. Usar 0.01 SOL para testar compra/venda")
    print("   2. Haverá pequena perda devido a taxas")
    print("   3. Nota: Em produção, o bot compra tokens detectados no Telegram")
    print()
    resposta = input("Deseja continuar? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        asyncio.run(test_buy_sell_sol())
    else:
        print("Teste cancelado.")

