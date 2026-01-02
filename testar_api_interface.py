"""
Script para testar se a API está retornando os dados corretos
"""
import requests
import json
import sys
import io

# Configura encoding para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def testar_api():
    """Testa se a API está retornando os novos campos"""
    try:
        print("Testando API da interface web...")
        print("=" * 60)
        
        # Testa endpoint de stats
        response = requests.get('http://localhost:5000/api/stats', timeout=5)
        if response.status_code != 200:
            print(f"❌ Erro: Status {response.status_code}")
            return
        
        stats = response.json()
        print("\n✅ API respondeu com sucesso!")
        print("\n📊 Campos retornados:")
        
        # Verifica campos novos
        campos_novos = [
            'today_tokens_bought',
            'total_tokens_bought',
            'today_profit',
            'score_analysis',
            'active_analysis'
        ]
        
        for campo in campos_novos:
            if campo in stats:
                print(f"  ✅ {campo}: {stats[campo]}")
            else:
                print(f"  ❌ {campo}: NÃO ENCONTRADO")
        
        # Mostra valores
        print("\n📈 Valores:")
        print(f"  Tokens comprados hoje: {stats.get('today_tokens_bought', 'N/A')}")
        print(f"  Total de tokens: {stats.get('total_tokens_bought', 'N/A')}")
        print(f"  Lucro hoje: {stats.get('today_profit', 'N/A')} SOL")
        print(f"  Análise por score: {len(stats.get('score_analysis', {}))} scores")
        print(f"  Tokens ativos: {len(stats.get('active_analysis', []))}")
        
        # Testa endpoint de trades ativos
        print("\n" + "=" * 60)
        print("Testando endpoint de trades ativos...")
        response2 = requests.get('http://localhost:5000/api/trades/active', timeout=5)
        if response2.status_code == 200:
            trades = response2.json()
            print(f"✅ {len(trades)} trades ativos encontrados")
            if len(trades) > 0:
                print(f"\nPrimeiro trade:")
                print(f"  Símbolo: {trades[0].get('symbol', 'N/A')}")
                print(f"  Amount SOL: {trades[0].get('amount_sol', 'N/A')}")
                print(f"  Score: {trades[0].get('score', 'N/A')}")
        else:
            print(f"❌ Erro: Status {response2.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ Teste concluído!")
        print("\n💡 Se todos os campos aparecem com ✅, a API está funcionando.")
        print("   Se a interface não mostra, pode ser cache do navegador.")
        print("   Tente: Ctrl+F5 ou limpar cache do navegador.")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor!")
        print("   Certifique-se de que o servidor está rodando em http://localhost:5000")
        print("   Execute: python run_all.py")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    testar_api()

