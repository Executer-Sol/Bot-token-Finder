"""
Bot que monitora tokens do site da Gangue em vez do Telegram
Mais rápido e direto
"""
import asyncio
from gangue_client import GangueClient
from jupiter_client import JupiterClient
from take_profit import TakeProfitManager
import config
from trade_tracker_integration import log_trade_bought, log_trade_update, log_trade_sold
from bot_control import get_bot_state
from last_token_detected import save_last_token
from logger import log_info, log_warning, log_error, log_success
from token_blacklist import get_blacklist_cache, is_blacklisted
from daily_loss_limit import check_daily_loss_limit, add_trade_result
from wallet_balance import get_wallet_balance
from datetime import datetime, timezone

class GangueTradingBot:
    def __init__(self):
        self.gangue = GangueClient(
            session_cookie=config.GANGUE_SESSION_COOKIE if config.GANGUE_SESSION_COOKIE else None,
            ga_cookie=config.GANGUE_GA_COOKIE if config.GANGUE_GA_COOKIE else None,
            cookies_file=config.GANGUE_COOKIES_FILE
        )
        self.jupiter = JupiterClient()
        self.tp_manager = TakeProfitManager(self.jupiter)
        self.active_trades = {}
        self.processed_tokens = set()  # Tokens já processados (para evitar duplicatas)
        self.bot_start_time = datetime.now(timezone.utc)
        self.running = False
    
    async def initialize(self):
        """Inicializa o bot"""
        log_success("Bot conectado à Gangue!")
        log_info(f"🕐 Bot iniciado às {self.bot_start_time.strftime('%H:%M:%S')} UTC")
        
        # Limpa último token detectado ao reiniciar
        import os
        last_token_file = 'last_token_detected.json'
        if os.path.exists(last_token_file):
            try:
                os.remove(last_token_file)
                log_info("🗑️  Último token antigo removido")
            except:
                pass
        
        # Carrega blacklist
        get_blacklist_cache()
    
    async def process_token(self, token_info):
        """Processa um token (mesma lógica do bot original)"""
        # Verifica estado do bot
        if not get_bot_state():
            return
        
        # Verifica blacklist
        if is_blacklisted(token_info.contract_address):
            log_warning(f"Token {token_info.symbol} está na blacklist - ignorado")
            return
        
        # Verifica limite de perda diário
        max_daily_loss = getattr(config, 'MAX_DAILY_LOSS_SOL', None)
        if max_daily_loss:
            if not check_daily_loss_limit():
                log_warning("Limite de perda diário atingido - compras pausadas")
                return
        
        # Verifica score
        if token_info.score < config.MIN_SCORE:
            log_info(f"⏭️  Token {token_info.symbol} com score {token_info.score} abaixo do mínimo ({config.MIN_SCORE})")
            return
        
        # Calcula valor baseado no score
        amount_sol = config.get_amount_by_score(token_info.score)
        
        if amount_sol == 0:
            log_info(f"⏭️  Token {token_info.symbol} com score {token_info.score} ignorado (fora do range ou score baixo desabilitado)")
            return
        
        # Verifica score máximo
        if token_info.score > config.MAX_SCORE:
            log_info(f"⏭️  Token {token_info.symbol} com score {token_info.score} acima do máximo ({config.MAX_SCORE})")
            return
        
        # Verifica saldo
        try:
            balance = await get_wallet_balance()
            required_sol = amount_sol + 0.01
            if balance['sol'] < required_sol:
                log_warning(f"Saldo insuficiente: {balance['sol']:.4f} SOL (precisa {required_sol:.4f} SOL)")
                return
        except Exception as e:
            log_error(f"Erro ao verificar saldo: {e}")
            return
        
        # Verifica janela de tempo
        # Como o site da Gangue não fornece horário de detecção, assumimos que foi detectado agora (0 minutos)
        # Isso permite comprar imediatamente se estiver dentro da janela de tempo
        max_time_minutes = config.get_max_time_by_score(token_info.score)
        if token_info.minutes_detected is None:
            # Se não tem horário, assume que foi detectado agora (0 minutos)
            token_info.minutes_detected = 0
            log_info(f"   ⏱️  Token detectado agora (site não fornece horário)")
        
        if token_info.minutes_detected > max_time_minutes:
            log_info(f"⏭️  Token {token_info.symbol} detectado há {token_info.minutes_detected} minutos - FORA da janela de compra (máx: {max_time_minutes}min)")
            return
        elif token_info.minutes_detected > 0:
            log_info(f"   ⏱️  Detectado há {token_info.minutes_detected} minutos (janela: {max_time_minutes}min)")
        
        # Verifica se já está negociando
        if token_info.contract_address in self.active_trades:
            log_info(f"⏭️  Token {token_info.symbol} já está sendo negociado")
            return
        
        log_info(f"\n🚀 Novo token detectado!")
        log_info(f"   Símbolo: {token_info.symbol}")
        log_info(f"   Score: {token_info.score}")
        log_info(f"   Preço: ${token_info.price}")
        log_info(f"   CA: {token_info.contract_address}")
        if token_info.minutes_detected is not None:
            log_info(f"   ⏱️  Tempo desde detecção: {token_info.minutes_detected} minutos")
        log_info(f"   💰 Investindo: {amount_sol} SOL (baseado no score)")
        
        # Salva último token detectado
        save_last_token(
            token_info.symbol,
            token_info.score,
            token_info.price,
            token_info.contract_address,
            token_info.minutes_detected
        )
        
        # Executa compra
        try:
            tx_signature, quote = await self.jupiter.buy_token(
                token_info.contract_address,
                amount_sol
            )
            
            log_success(f"Compra realizada! TX: {tx_signature}")
            
            # Obtém valores reais da transação
            real_amount_sol = quote.get('real_in_amount_sol', amount_sol)
            amount_tokens = quote.get('real_out_amount_tokens', 0)
            
            # Preço de entrada em USD (do Telegram/Gangue quando detectado)
            entry_price = token_info.price
            
            # Calcula também o preço em SOL/token
            if real_amount_sol > 0 and amount_tokens > 0:
                entry_price_sol = real_amount_sol / (amount_tokens / 1e9) if amount_tokens > 0 else 0
            else:
                entry_price_sol = 0
            
            log_info(f"   💰 Valores reais da transação:")
            log_info(f"      SOL gasto REAL: {real_amount_sol:.6f} SOL")
            log_info(f"      Tokens recebidos REAL: {amount_tokens}")
            log_info(f"      Preço de entrada (USD): ${entry_price:.10f} (do Gangue quando detectado)")
            log_info(f"      Preço de entrada (SOL/token): {entry_price_sol:.10f}")
            
            # Adiciona ao take profit manager
            self.tp_manager.add_position(
                token_info.contract_address,
                token_info.symbol,
                amount_tokens,
                entry_price,
                token_info.score
            )
            
            self.active_trades[token_info.contract_address] = {
                'symbol': token_info.symbol,
                'tx': tx_signature,
                'entry_price': entry_price
            }
            
            # Salva no histórico
            log_trade_bought(
                token_info.symbol,
                token_info.contract_address,
                entry_price,
                real_amount_sol,
                token_info.score,
                tx_signature,
                amount_tokens
            )
            
            log_info(f"📊 Posição monitorada: {token_info.symbol} @ ${entry_price:.10f}")
        
        except Exception as e:
            log_error(f"Erro ao comprar token {token_info.symbol}: {e}")
    
    async def monitor_loop(self):
        """Loop principal de monitoramento"""
        self.running = True
        log_info(f"🔄 Iniciando monitoramento da Gangue (intervalo: {config.GANGUE_POLL_INTERVAL}s)")
        
        while self.running:
            try:
                if not get_bot_state():
                    await asyncio.sleep(config.GANGUE_POLL_INTERVAL)
                    continue
                
                # Busca tokens mais recentes
                tokens = await self.gangue.get_latest_tokens(limit=20)
                
                for token_info in tokens:
                    # Evita processar o mesmo token duas vezes
                    token_key = f"{token_info.contract_address}_{token_info.symbol}"
                    if token_key in self.processed_tokens:
                        continue
                    
                    # Registra horário de detecção (horário do computador quando detectado)
                    from datetime import datetime, timezone
                    if not hasattr(token_info, 'detected_at') or token_info.detected_at is None:
                        # Primeira vez que vê este token - registra horário atual do computador
                        token_info.detected_at = datetime.now(timezone.utc)
                        token_info.minutes_detected = 0
                        log_info(f"🕐 Token {token_info.symbol} detectado às {token_info.detected_at.strftime('%H:%M:%S')} UTC (horário do computador)")
                    
                    # Marca como processado
                    self.processed_tokens.add(token_key)
                    
                    # Processa token
                    await self.process_token(token_info)
                
                # Limita tamanho do set de processados (evita memory leak)
                if len(self.processed_tokens) > 1000:
                    # Mantém apenas os últimos 500
                    self.processed_tokens = set(list(self.processed_tokens)[-500:])
                
                await asyncio.sleep(config.GANGUE_POLL_INTERVAL)
                
            except Exception as e:
                log_error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(config.GANGUE_POLL_INTERVAL)
    
    async def start(self):
        """Inicia o bot"""
        await self.initialize()
        
        # TakeProfitManager não precisa de start() - funciona automaticamente quando add_position() é chamado
        
        # Inicia loop de monitoramento
        await self.monitor_loop()
    
    async def stop(self):
        """Para o bot"""
        self.running = False
        
        # Cancela todas as tarefas de monitoramento do TakeProfitManager
        for task in self.tp_manager.monitoring_tasks.values():
            task.cancel()
        
        # Aguarda cancelamento
        for task in self.tp_manager.monitoring_tasks.values():
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        await self.gangue.close()
        await self.jupiter.close()

async def main():
    """Função principal"""
    bot = GangueTradingBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        log_info("🛑 Bot interrompido")
    finally:
        await bot.stop()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

