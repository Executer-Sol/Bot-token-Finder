"""
Sistema de backup automático em background (não bloqueia o bot)
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
import threading
import time

BACKUP_DIR = Path('backups')
BACKUP_DIR.mkdir(exist_ok=True)

# Arquivos importantes para backup
FILES_TO_BACKUP = [
    'trades_history.json',
    'bot_state.json',
    'last_token_detected.json',
    'token_blacklist.json',
    'daily_loss.json'
]

def create_backup():
    """Cria backup dos arquivos importantes"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_folder = BACKUP_DIR / timestamp
        backup_folder.mkdir(exist_ok=True)
        
        for file_name in FILES_TO_BACKUP:
            source = Path(file_name)
            if source.exists():
                dest = backup_folder / file_name
                shutil.copy2(source, dest)
        
        # Limpa backups antigos (mantém últimos 7 dias)
        cleanup_old_backups(days=7)
        
        return True
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return False

def cleanup_old_backups(days=7):
    """Remove backups mais antigos que X dias"""
    try:
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for backup_folder in BACKUP_DIR.iterdir():
            if backup_folder.is_dir():
                if backup_folder.stat().st_mtime < cutoff_time:
                    shutil.rmtree(backup_folder)
    except Exception as e:
        # Ignora erros de limpeza
        pass

def start_backup_scheduler(interval_hours=24):
    """Inicia scheduler de backup em thread separada"""
    def backup_loop():
        while True:
            try:
                time.sleep(interval_hours * 60 * 60)  # Espera X horas
                create_backup()
            except Exception:
                # Continua mesmo se der erro
                pass
    
    thread = threading.Thread(target=backup_loop, daemon=True)
    thread.start()
    return thread

# Inicia backup automático ao importar (se quiser usar)
# start_backup_scheduler(interval_hours=24)











