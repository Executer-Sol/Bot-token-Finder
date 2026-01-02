"""
Sistema de logging assíncrono (não bloqueia o bot)
"""
import logging
import asyncio
from datetime import datetime
from pathlib import Path
import queue
import threading

# Cria diretório de logs se não existir
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# Fila para logs assíncronos
log_queue = queue.Queue()

class AsyncFileHandler(logging.Handler):
    """Handler que escreve logs em arquivo de forma assíncrona"""
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._write_logs, daemon=True)
        self.worker_thread.start()
    
    def emit(self, record):
        """Adiciona log na fila (não bloqueia)"""
        try:
            self.queue.put(self.format(record), block=False)
        except queue.Full:
            # Se a fila estiver cheia, ignora (não bloqueia)
            pass
    
    def _write_logs(self):
        """Thread worker que escreve logs no arquivo"""
        while True:
            try:
                log_message = self.queue.get(timeout=1)
                with open(self.filename, 'a', encoding='utf-8') as f:
                    f.write(log_message + '\n')
                    f.flush()
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                # Ignora erros para não bloquear
                pass

def setup_logger():
    """Configura o logger global"""
    logger = logging.getLogger('trading_bot')
    logger.setLevel(logging.INFO)
    
    # Remove handlers existentes
    logger.handlers.clear()
    
    # Handler para arquivo (assíncrono)
    log_file = LOG_DIR / f'bot_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = AsyncFileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)
    
    # Handler para console (mantém output visual no terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console_handler)
    
    # Previne duplicação de logs (evita que root logger também processe)
    logger.propagate = False
    
    return logger

# Logger global (singleton)
_bot_logger = None

def get_logger():
    """Retorna logger singleton"""
    global _bot_logger
    if _bot_logger is None:
        _bot_logger = setup_logger()
    return _bot_logger

bot_logger = get_logger()

def log_info(message: str):
    """Log de informação (não bloqueia)"""
    bot_logger.info(message)
    # Não faz print aqui - o console handler já mostra no terminal

def log_warning(message: str):
    """Log de aviso (não bloqueia)"""
    bot_logger.warning(f"⚠️  {message}")
    # Console handler já mostra no terminal

def log_error(message: str):
    """Log de erro (não bloqueia)"""
    bot_logger.error(f"❌ {message}")
    # Console handler já mostra no terminal

def log_success(message: str):
    """Log de sucesso (não bloqueia)"""
    bot_logger.info(f"✅ {message}")
    # Console handler já mostra no terminal

