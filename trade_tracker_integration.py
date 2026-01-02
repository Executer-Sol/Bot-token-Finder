"""
Módulo para integrar o tracker com o bot
Importe este módulo no bot.py para salvar trades automaticamente
"""
from web_interface import TradeTracker
import threading
from daily_loss_limit import add_trade_result

# Instância global do tracker
_tracker = None
_tracker_lock = threading.Lock()

def get_tracker():
    """Retorna instância do tracker (singleton)"""
    global _tracker
    if _tracker is None:
        with _tracker_lock:
            if _tracker is None:
                _tracker = TradeTracker()
    return _tracker

def log_trade_bought(symbol: str, ca: str, entry_price: float, 
                    amount_sol: float, score: int, tx: str, amount_tokens: int = None):
    """Log quando um trade é comprado
    Args:
        amount_sol: Quantidade em SOL
        amount_tokens: Quantidade de tokens comprados (raw amount) - não usado por enquanto
    """
    tracker = get_tracker()
    tracker.add_active_trade(symbol, ca, entry_price, amount_sol, score, tx)
    print(f"📝 Trade salvo no histórico: {symbol} ({amount_sol} SOL)")
    
    # Marca token como comprado no tracker
    try:
        from detected_tokens_tracker import mark_token_as_bought
        mark_token_as_bought(ca)
    except:
        pass  # Não bloqueia se der erro

def log_trade_update(ca: str, current_price: float = None,
                    remaining_percent: float = None,
                    tps_executed: list = None):
    """Log quando um trade é atualizado (preço, vendas parciais)"""
    tracker = get_tracker()
    tracker.update_active_trade(ca, current_price, remaining_percent, tps_executed)

def log_trade_sold(ca: str, final_price: float = None, total_sold_percent: float = 100.0, 
                   reason: str = None, time_to_peak: float = None, time_to_sell: float = None,
                   peak_multiple: float = None, real_sol_received: float = None):
    """Log quando um trade é totalmente vendido
    Args:
        reason: Motivo da venda (ex: 'stop_loss_time', 'take_profit', etc)
        time_to_peak: Tempo em minutos até atingir o pico
        time_to_sell: Tempo em minutos até vender completamente
        peak_multiple: Maior múltiplo atingido
        real_sol_received: SOL real recebido da venda (baseado no saldo da carteira)
    """
    tracker = get_tracker()
    trade = tracker.move_to_sold(ca, final_price, total_sold_percent, reason, 
                                  time_to_peak, time_to_sell, peak_multiple, real_sol_received)
    if trade:
        # Adiciona resultado ao limite diário (assíncrono - não bloqueia)
        try:
            # Usa profit_loss_sol diretamente (ou converte de USDC se for trade antigo)
            profit_loss_sol = trade.get('profit_loss_sol', trade.get('profit_loss_usdc', 0) / 100.0)
            add_trade_result(profit_loss_sol)
        except:
            pass  # Não bloqueia se der erro
        profit_loss = trade.get('profit_loss_sol', trade.get('profit_loss_usdc', 0) / 100.0)
        print(f"✅ Trade vendido salvo no histórico: {trade['symbol']} - Lucro/Perda: {profit_loss:.4f} SOL")

