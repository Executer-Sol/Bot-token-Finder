"""
Script para rodar o bot em modo servidor (background)
Use este script para rodar o bot continuamente
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_bot():
    """Roda o bot em loop (reinicia se crashar)"""
    bot_dir = Path(__file__).parent
    
    print("="*70)
    print("🤖 Bot Trading - Modo Servidor")
    print("="*70)
    print("\n📌 O bot está rodando em modo servidor")
    print("🌐 Acesse a interface web para ativar/desativar")
    print("📍 Interface: http://localhost:5000")
    print("\n⚠️  Mantenha este terminal aberto")
    print("🛑 Pressione Ctrl+C para parar\n")
    print("="*70 + "\n")
    
    while True:
        try:
            # Roda o bot
            process = subprocess.Popen(
                [sys.executable, str(bot_dir / "bot.py")],
                cwd=str(bot_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Mostra output em tempo real
            for line in process.stdout:
                print(line, end='')
            
            # Espera processo terminar
            process.wait()
            
            # Se chegou aqui, o processo terminou
            if process.returncode != 0:
                print(f"\n⚠️  Bot terminou com código {process.returncode}")
                print("🔄 Reiniciando em 5 segundos...\n")
                time.sleep(5)
            else:
                print("\n✅ Bot terminou normalmente")
                break
                
        except KeyboardInterrupt:
            print("\n\n🛑 Parando bot servidor...")
            if 'process' in locals():
                process.terminate()
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("🔄 Reiniciando em 10 segundos...\n")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()

