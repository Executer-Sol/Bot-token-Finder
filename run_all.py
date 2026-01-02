"""
Roda Bot + Interface Web no mesmo terminal
"""
import subprocess
import sys
import os
import threading
import time
from pathlib import Path

def run_web_interface():
    """Roda interface web em janela separada"""
    bot_dir = Path(__file__).parent
    if sys.platform == 'win32':
        # Inicia em nova janela do CMD
        process = subprocess.Popen(
            ['cmd', '/c', 'start', 'Interface Web', 'cmd', '/k', 
             f'cd /d "{bot_dir}" && python run_web.py'],
            cwd=str(bot_dir)
        )
    else:
        # Linux/Mac
        process = subprocess.Popen(
            [sys.executable, str(bot_dir / "web_interface.py")],
            cwd=str(bot_dir)
        )
    return process

def run_all():
    """Roda tudo"""
    print("="*70)
    print("Bot Trading - TUDO EM UM TERMINAL")
    print("="*70)
    print("\nInterface Web: http://localhost:5000")
    print("Bot: Monitorando Telegram")
    print("\nPressione Ctrl+C para parar TUDO\n")
    print("="*70 + "\n")
    
    # Inicia interface web em janela separada
    print("[INFO] Iniciando Interface Web em janela separada...")
    web_process = run_web_interface()
    time.sleep(4)  # Aguarda interface iniciar
    print("[INFO] Interface Web iniciada! Acesse: http://localhost:5000\n")
    print("-"*70)
    print("[INFO] Iniciando Bot...\n")
    print("-"*70 + "\n")
    
    # Roda bot no processo principal (mostra output direto)
    bot_dir = Path(__file__).parent
    
    # Verifica se deve usar Gangue ou Telegram
    from dotenv import load_dotenv
    import os
    load_dotenv()
    # Só usa Gangue se explicitamente 'true' no .env, caso contrário usa Telegram
    use_gangue = os.getenv('USE_GANGUE', '').lower() == 'true'
    
    bot_file = "gangue_bot.py" if use_gangue else "bot.py"
    bot_name = "Gangue" if use_gangue else "Telegram"
    
    print(f"[INFO] Usando fonte: {bot_name}")
    
    try:
        bot_process = subprocess.run(
            [sys.executable, str(bot_dir / bot_file)],
            cwd=str(bot_dir)
        )
    except KeyboardInterrupt:
        print("\n\n[INFO] Parando todos os serviços...")
        if web_process:
            web_process.terminate()
        print("[INFO] Servicos parados")

if __name__ == "__main__":
    run_all()
