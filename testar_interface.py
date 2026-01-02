"""
Testa se a interface web está funcionando
"""
import requests
import sys
import io

# Configura encoding para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print("TESTANDO INTERFACE WEB")
print("="*70)
print()

base_url = "http://localhost:5000"

endpoints = [
    "/",
    "/api/trades/active",
    "/api/trades/sold",
    "/api/stats",
    "/api/bot/state",
    "/api/last-token",
    "/api/wallet-balance"
]

for endpoint in endpoints:
    try:
        url = base_url + endpoint
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {endpoint}: OK (Status {response.status_code})")
        else:
            print(f"⚠️  {endpoint}: Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint}: Servidor não está rodando ou não está acessível")
        print(f"   Execute: python run_web.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ {endpoint}: Erro - {e}")

print()
print("="*70)
print("TESTE CONCLUIDO")
print("="*70)
