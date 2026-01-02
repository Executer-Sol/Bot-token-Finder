"""
Script de diagnóstico para problemas de DNS com Jupiter API
"""
import socket
import sys

def test_dns():
    """Testa resolução de DNS"""
    domains = [
        'quote-api.jup.ag',
        'www.google.com',
        'api.mainnet-beta.solana.com'
    ]
    
    print("="*70)
    print("DIAGNOSTICO DE DNS")
    print("="*70)
    print()
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"OK: {domain} -> {ip}")
        except socket.gaierror as e:
            print(f"ERRO: {domain} - {e}")
        except Exception as e:
            print(f"ERRO: {domain} - {e}")
    
    print()
    print("="*70)
    print("SOLUCOES SUGERIDAS:")
    print("="*70)
    print()
    print("1. MUDAR DNS:")
    print("   - Vá em Configuracoes > Rede e Internet > Wi-Fi/Ethernet")
    print("   - Clique no adaptador ativo > Propriedades")
    print("   - IPv4 > Propriedades > Use os seguintes enderecos de servidor DNS:")
    print("     DNS preferencial: 8.8.8.8")
    print("     DNS alternativo: 8.8.4.4")
    print()
    print("2. FLUSH DNS:")
    print("   Execute como Administrador:")
    print("   ipconfig /flushdns")
    print()
    print("3. VERIFICAR FIREWALL:")
    print("   - Windows Defender Firewall pode estar bloqueando")
    print("   - Antivirus pode estar bloqueando")
    print()
    print("4. PROXY/VPN:")
    print("   - Desabilite VPN temporariamente")
    print("   - Verifique configuracoes de proxy")
    print()

if __name__ == "__main__":
    test_dns()

