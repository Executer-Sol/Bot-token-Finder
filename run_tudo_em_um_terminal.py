"""
Roda Interface Web + Bot em um único terminal
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_all_in_one():
    """Roda interface web e bot no mesmo terminal"""
    bot_dir = Path(__file__).parent
    
    print("="*70)
    print("🤖 Bot Trading - Interface Web + Bot em UM Terminal")
    print("="*70)
    print("\n⚠️  IMPORTANTE:")
    print("   - Interface Web será iniciada primeiro")
    print("   - Depois o Bot será iniciado")
    print("   - Ambos rodarão juntos neste terminal")
    print("\n📍 Interface Web: http://localhost:5000")
    print("\n🛑 Pressione Ctrl+C para parar TUDO\n")
    print("="*70 + "\n")
    
    # Inicia interface web em background
    print("🌐 Iniciando Interface Web...")
    web_process = subprocess.Popen(
        [sys.executable, str(bot_dir.parent / "scripts" / "run_web.py")],
        cwd=str(bot_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Aguarda interface web iniciar
    time.sleep(3)
    
    print("✅ Interface Web iniciada!")
    print("\n🤖 Iniciando Bot Trading...")
    print("-"*70 + "\n")
    
    # Inicia bot (este vai rodar em foreground e mostrar output)
    try:
        bot_process = subprocess.Popen(
            [sys.executable, str(bot_dir / "bot.py")],
            cwd=str(bot_dir),
            text=True,
            bufsize=1
        )
        
        # Mostra output da interface web em uma thread separada seria complexo
        # Por enquanto, o bot roda em foreground e a interface em background
        
        # Espera processos terminarem
        try:
            # Monitora output da interface web
            for line in web_process.stdout:
                if line:
                    print(f"[WEB] {line}", end='')
        except KeyboardInterrupt:
            print("\n\n🛑 Parando todos os serviços...")
            web_process.terminate()
            bot_process.terminate()
            web_process.wait()
            bot_process.wait()
            print("✅ Todos os serviços parados")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Parando todos os serviços...")
        web_process.terminate()
        if 'bot_process' in locals():
            bot_process.terminate()
        web_process.wait()
        print("✅ Serviços parados")

if __name__ == "__main__":
    run_all_in_one()

