"""
Script para verificar se a interface está retornando os dados corretos
"""
import requests
import json

try:
    # Testa a API de stats
    response = requests.get('http://localhost:5000/api/stats', timeout=5)
    if response.status_code == 200:
        stats = response.json()
        print("=" * 60)
        print("DADOS RETORNADOS PELA API /api/stats")
        print("=" * 60)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        print("\n" + "=" * 60)
        print("VERIFICACAO:")
        print("=" * 60)
        
        if 'today_tokens_bought' in stats:
            print(f"[OK] today_tokens_bought: {stats['today_tokens_bought']}")
        else:
            print("[ERRO] today_tokens_bought NAO encontrado - Servidor precisa ser reiniciado!")
            
        if 'total_tokens_bought' in stats:
            print(f"[OK] total_tokens_bought: {stats['total_tokens_bought']}")
        else:
            print("[ERRO] total_tokens_bought NAO encontrado - Servidor precisa ser reiniciado!")
            
        if 'score_analysis' in stats:
            print(f"[OK] score_analysis: {len(stats['score_analysis'])} scores")
        else:
            print("[ERRO] score_analysis NAO encontrado - Servidor precisa ser reiniciado!")
            
        if 'active_analysis' in stats:
            print(f"[OK] active_analysis: {len(stats['active_analysis'])} tokens ativos")
        else:
            print("[ERRO] active_analysis NAO encontrado - Servidor precisa ser reiniciado!")
            
    else:
        print(f"[ERRO] Erro ao acessar API: Status {response.status_code}")
        print(f"Resposta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("[ERRO] Nao foi possivel conectar ao servidor web")
    print("   Certifique-se de que o servidor esta rodando em http://localhost:5000")
    print("   Execute: python run_all.py ou python run_web.py")
except Exception as e:
    print(f"[ERRO] Erro: {e}")

