"""
Inicia a interface web
"""
import sys
import io

# Configura encoding para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*70)
print("🌐 Interface Web do Bot Trading")
print("="*70)
print("\n📍 Acesse no navegador: http://localhost:5000")
print("\n📊 O dashboard mostrará:")
print("   - Tokens ativos (segurando)")
print("   - Tokens vendidos (histórico)")
print("   - Estatísticas e lucros/perdas")
print("\n⏱️  Interface atualiza automaticamente a cada 5 segundos")
print("\n⚠️  Mantenha esta janela aberta para o servidor funcionar")
print("="*70 + "\n")

# Importa e roda o app
if __name__ == '__main__':
    try:
        from web_interface import app
        print("\n✅ Servidor iniciando...\n")
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=True)
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}\n")
        import traceback
        traceback.print_exc()

