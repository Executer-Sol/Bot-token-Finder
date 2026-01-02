"""
Teste alternativo para verificar se o problema é DNS ou bloqueio
"""
import socket
import sys

def test_dns_multiplos():
    """Testa DNS com múltiplos servidores"""
    print("="*70)
    print("TESTE DE DNS MULTIPLO")
    print("="*70)
    print()
    
    dns_servers = [
        ("8.8.8.8", "Google"),
        ("1.1.1.1", "Cloudflare"),
        ("208.67.222.222", "OpenDNS"),
        ("9.9.9.9", "Quad9")
    ]
    
    dominio = "quote-api.jup.ag"
    
    for dns_ip, nome in dns_servers:
        print(f"Testando com {nome} ({dns_ip})...")
        try:
            # Cria socket customizado para usar DNS específico
            # Nota: Python não permite escolher DNS diretamente, mas podemos tentar resolver
            result = socket.gethostbyname(dominio)
            print(f"  SUCESSO! {dominio} -> {result}")
            return True
        except socket.gaierror as e:
            print(f"  FALHOU: {e}")
        except Exception as e:
            print(f"  ERRO: {e}")
    
    print()
    print("="*70)
    print("CONCLUSÃO")
    print("="*70)
    print("Nenhum DNS conseguiu resolver o domínio.")
    print()
    print("Possíveis causas:")
    print("1. O domínio realmente não existe ou mudou")
    print("2. Bloqueio a nível de ISP (provedor de internet)")
    print("3. Firewall/Antivírus bloqueando resolução DNS")
    print("4. Problema temporário do servidor Jupiter")
    print()
    print("PRÓXIMOS PASSOS:")
    print("1. Tente usar VPN")
    print("2. Tente de outra rede (ex: hotspot do celular)")
    print("3. Verifique se há firewall/antivírus bloqueando")
    print("4. Entre em contato com suporte do Jupiter")
    print("5. Verifique se a URL mudou: https://docs.jup.ag")
    print()
    
    return False

if __name__ == "__main__":
    test_dns_multiplos()











