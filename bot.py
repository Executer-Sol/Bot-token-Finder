import asyncio
from telethon import TelegramClient, events
from message_parser import parse_token_message
from jupiter_client import JupiterClient
from take_profit import TakeProfitManager
import config
from trade_tracker_integration import log_trade_bought, log_trade_update, log_trade_sold
from bot_control import get_bot_state
from last_token_detected import save_last_token
from detected_tokens_tracker import add_detected_token, mark_token_as_bought
from logger import log_info, log_warning, log_error, log_success
from token_blacklist import get_blacklist_cache, is_blacklisted
from daily_loss_limit import check_daily_loss_limit, add_trade_result
from wallet_balance import get_wallet_balance

class TradingBot:
    def __init__(self):
        self.client = TelegramClient(
            'session',
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH
        )
        self.jupiter = JupiterClient()
        self.tp_manager = TakeProfitManager(self.jupiter)
        self.active_trades = {}
        self.bot_was_enabled = True  # Estado anterior do bot
    
    async def initialize(self):
        """Initialize Telegram client"""
        import os
        import time
        
        # Verifica e remove journal file se existir (pode causar lock)
        journal_file = 'session.session-journal'
        if os.path.exists(journal_file):
            try:
                os.remove(journal_file)
                log_info("Arquivo journal removido")
            except:
                pass
        
        # Tenta conectar com retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.client.start(phone=config.TELEGRAM_PHONE)
                log_success("Bot conectado ao Telegram!")
                # Carrega blacklist no início (cache rápido)
                get_blacklist_cache()
                return
            except Exception as e:
                if "database is locked" in str(e) or "OperationalError" in str(type(e).__name__):
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        log_warning(f"Banco de dados bloqueado. Tentando novamente em {wait_time} segundos... (tentativa {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        # Tenta remover journal novamente
                        if os.path.exists(journal_file):
                            try:
                                os.remove(journal_file)
                            except:
                                pass
                    else:
                        log_error("Erro: Banco de dados ainda está bloqueado. Verifique se há outra instância do bot rodando.")
                        log_error("Solução: Feche todas as instâncias do bot e tente novamente.")
                        raise
                else:
                    raise
    
    async def on_new_message(self, event):
        """Handle new message from Telegram channel"""
        message = event.message.text
        
        # Debug: mostra mensagem recebida (apenas se tiver formato de token parcial)
        if message and ('#' in message and 'Score:' in message):
            # Log apenas se parece ser token (para não poluir logs)
            log_info(f"📨 Mensagem recebida ({len(message)} chars): {message[:200]}...")
        
        # Parse token information
        token_info = parse_token_message(message)
        
        if not token_info:
            # Se parece ser token mas parse falhou, log para debug
            if message and ('#' in message and 'Score:' in message):
                log_warning(f"⚠️  Parse falhou para mensagem com formato de token")
                log_warning(f"   Mensagem: {message[:300]}")
            return
        
        # Calcula tempo desde que a mensagem foi enviada no Telegram (timestamp da mensagem)
        # Usa o horário que a mensagem entrou no chat (ex: 18:31, 20:27) e calcula minutos desde então
        from datetime import datetime, timezone
        message_date = event.message.date
        detected_at = None
        if message_date:
            now = datetime.now(timezone.utc)
            if message_date.tzinfo is None:
                # Se não tem timezone, assume UTC
                message_date = message_date.replace(tzinfo=timezone.utc)
            detected_at = message_date
            time_diff = now - message_date
            minutes_since_message = int(time_diff.total_seconds() / 60)
            # Usa o tempo desde que a mensagem foi enviada no Telegram (não o tempo do texto)
            token_info.minutes_detected = minutes_since_message
            log_info(f"   ⏱️  Mensagem enviada há {minutes_since_message} minutos (timestamp do Telegram: {message_date.strftime('%H:%M')})")
        
        # Salva último token detectado (SEMPRE, mesmo se bot estiver desativado)
        save_last_token(
            token_info.symbol,
            token_info.score,
            token_info.price,
            token_info.contract_address,
            token_info.minutes_detected,
            detected_at
        )
        
        # Adiciona ao tracker de tokens detectados (SEMPRE, mesmo se bot estiver desativado)
        add_detected_token(
            token_info.symbol,
            token_info.score,
            token_info.price,
            token_info.contract_address,
            token_info.minutes_detected,
            detected_at
        )
        
        # Verifica estado do bot (pode ser alterado via interface web)
        if not get_bot_state():
            # Não mostra mensagem para cada token quando desativado
            # A mensagem principal já foi mostrada pelo monitor
            return
        
        # Verifica blacklist (O(1) - muito rápido)
        if is_blacklisted(token_info.contract_address):
            log_warning(f"Token {token_info.symbol} está na blacklist - ignorado")
            return
        
        # Verifica limite de perda diário (rápido - apenas leitura)
        max_daily_loss = getattr(config, 'MAX_DAILY_LOSS_SOL', None)
        if max_daily_loss:
            limit_reached, stats = check_daily_loss_limit(max_daily_loss)
            if limit_reached:
                log_warning(f"Limite de perda diário atingido! Perda: {stats['total_loss']:.4f} SOL")
                return
        
        # Recarrega config antes de usar (para pegar valores atualizados via interface web)
        config.reload_config()
        
        # Get amount based on score (em SOL)
        amount_sol = config.get_amount_by_score(token_info.score)
        
        if amount_sol == 0:
            log_info(f"⏭️  Token {token_info.symbol} com score {token_info.score} ignorado (fora do range ou score baixo desabilitado)")
            return
        
        # Check if score is within max range
        if token_info.score > config.MAX_SCORE:
            log_info(f"⏭️  Token {token_info.symbol} com score {token_info.score} acima do máximo ({config.MAX_SCORE})")
            return
        
        # Verifica saldo rapidamente (antes de comprar)
        try:
            balance = await get_wallet_balance()
            required_sol = amount_sol + 0.01  # +0.01 para taxas
            if balance['sol'] < required_sol:
                log_warning(f"Saldo insuficiente: {balance['sol']:.4f} SOL (precisa {required_sol:.4f} SOL)")
                return
        except Exception as e:
            log_error(f"Erro ao verificar saldo: {e}")
            # Continua mesmo assim (não bloqueia)
        
        # Check time window for buying (regra de timing)
        max_time_minutes = config.get_max_time_by_score(token_info.score)
        if token_info.minutes_detected is not None:
            if token_info.minutes_detected > max_time_minutes:
                log_info(f"⏭️  Token {token_info.symbol} detectado há {token_info.minutes_detected} minutos - FORA da janela de compra (máx: {max_time_minutes}min)")
                return
            elif token_info.minutes_detected > 0:
                log_info(f"   ⏱️  Detectado há {token_info.minutes_detected} minutos (janela: {max_time_minutes}min)")
        
        # Check if we already have this token
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
        
        # Execute buy
        try:
            tx_signature, quote = await self.jupiter.buy_token(
                token_info.contract_address,
                amount_sol
            )
            
            log_success(f"Compra realizada! TX: {tx_signature}")
            
            # Get valores reais da transação Jupiter
            amount_tokens = int(quote.get('outAmount', 0))
            real_amount_sol = quote.get('real_in_amount_sol', amount_sol)
            
            # SEMPRE usa preço do Telegram para entrada (mais confiável para tokens novos)
            # O preço do Telegram já vem parseado corretamente da mensagem
            # O cálculo da Jupiter não é confiável porque não sabemos os decimais do token
            entry_price = token_info.price
            
            if entry_price <= 0:
                log_error(f"   ⚠️  Preço do Telegram inválido ({entry_price}), tentando usar preço da Jupiter...")
                real_price = quote.get('calculated_price', 0)
                if real_price > 0 and real_price >= 1e-8:
                    entry_price = real_price
                else:
                    log_error(f"   ❌ Preço da Jupiter também inválido ({real_price:.10f}), usando fallback")
                    # Fallback: calcula baseado em SOL gasto (aproximado)
                    if amount_tokens > 0:
                        # Assume 9 decimais (padrão Solana) - pode não ser exato
                        entry_price = (real_amount_sol / (amount_tokens / 1e9)) if amount_tokens > 0 else 0
                    if entry_price <= 0:
                        log_error(f"   ❌ Não foi possível determinar preço de entrada!")
                        entry_price = 0.0001  # Fallback mínimo para não quebrar
            
            log_info(f"   💰 Valores reais da transação:")
            log_info(f"      SOL gasto: {real_amount_sol:.6f} SOL")
            log_info(f"      Tokens recebidos: {amount_tokens}")
            log_info(f"      Preço de entrada: ${entry_price:.10f} (Telegram)")
            
            # Add to take profit manager com preço real
            self.tp_manager.add_position(
                token_info.contract_address,
                token_info.symbol,
                amount_tokens,
                entry_price,  # Usa preço real da Jupiter
                token_info.score
            )
            
            self.active_trades[token_info.contract_address] = {
                'symbol': token_info.symbol,
                'tx': tx_signature,
                'entry_price': entry_price  # Preço real
            }
            
            # Salva no histórico para interface web com valores reais
            log_trade_bought(
                token_info.symbol,
                token_info.contract_address,
                entry_price,  # Preço real da Jupiter
                real_amount_sol,  # SOL real gasto
                token_info.score,
                tx_signature
            )
            
            log_info(f"📊 Posição monitorada: {token_info.symbol} @ ${entry_price:.10f} (preço real Jupiter)")
        
        except Exception as e:
            log_error(f"Erro ao comprar token {token_info.symbol}: {e}")
    
    async def _monitor_bot_state(self):
        """Monitora estado do bot e mostra mensagens quando muda"""
        import sys
        import io
        
        # Garante encoding UTF-8 para Windows
        if sys.stdout.encoding != 'utf-8':
            try:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            except:
                pass
        
        config_reload_counter = 0
        # Armazena valores anteriores para detectar mudanças
        prev_amount_15_17 = config.AMOUNT_SOL_15_17
        prev_amount_18_19 = config.AMOUNT_SOL_18_19
        prev_amount_20_21 = config.AMOUNT_SOL_20_21
        prev_amount_low = config.AMOUNT_SOL_LOW
        prev_time_15_17 = config.MAX_TIME_MINUTES_15_17
        prev_time_18_19 = config.MAX_TIME_MINUTES_18_19
        prev_time_20_21 = config.MAX_TIME_MINUTES_20_21
        prev_enable_low = config.ENABLE_LOW_SCORE
        
        while True:
            try:
                await asyncio.sleep(2)  # Verifica a cada 2 segundos
                current_state = get_bot_state()
                
                # Recarrega configurações a cada 10 segundos (5 iterações de 2s)
                config_reload_counter += 1
                if config_reload_counter >= 5:
                    config_reload_counter = 0
                    try:
                        config.reload_config()
                        
                        # Verifica se houve mudanças
                        if (prev_amount_15_17 != config.AMOUNT_SOL_15_17 or
                            prev_amount_18_19 != config.AMOUNT_SOL_18_19 or
                            prev_amount_20_21 != config.AMOUNT_SOL_20_21 or
                            prev_amount_low != config.AMOUNT_SOL_LOW or
                            prev_time_15_17 != config.MAX_TIME_MINUTES_15_17 or
                            prev_time_18_19 != config.MAX_TIME_MINUTES_18_19 or
                            prev_time_20_21 != config.MAX_TIME_MINUTES_20_21 or
                            prev_enable_low != config.ENABLE_LOW_SCORE):
                            changed = True
                            
                            # Atualiza valores anteriores
                            prev_amount_15_17 = config.AMOUNT_SOL_15_17
                            prev_amount_18_19 = config.AMOUNT_SOL_18_19
                            prev_amount_20_21 = config.AMOUNT_SOL_20_21
                            prev_amount_low = config.AMOUNT_SOL_LOW
                            prev_time_15_17 = config.MAX_TIME_MINUTES_15_17
                            prev_time_18_19 = config.MAX_TIME_MINUTES_18_19
                            prev_time_20_21 = config.MAX_TIME_MINUTES_20_21
                            prev_enable_low = config.ENABLE_LOW_SCORE
                            
                            # Mostra mensagem de atualização
                            log_success("\n" + "="*70)
                            log_success("⚙️  CONFIGURAÇÕES ATUALIZADAS!")
                            log_info("💰 Valores por score:")
                            log_info(f"   Score 15-17: {config.AMOUNT_SOL_15_17} SOL - Máx {config.MAX_TIME_MINUTES_15_17}min")
                            log_info(f"   Score 18-19: {config.AMOUNT_SOL_18_19} SOL - Máx {config.MAX_TIME_MINUTES_18_19}min")
                            log_info(f"   Score 20-21: {config.AMOUNT_SOL_20_21} SOL - Máx {config.MAX_TIME_MINUTES_20_21}min")
                            if config.ENABLE_LOW_SCORE:
                                log_info(f"   Score <15: {config.AMOUNT_SOL_LOW} SOL")
                            log_info("="*70 + "\n")
                    except Exception as e:
                        # Se falhar, continua sem recarregar
                        pass
                
                # Se estado mudou, mostra mensagem
                if current_state != self.bot_was_enabled:
                    self.bot_was_enabled = current_state
                    if current_state:
                        log_success("\n" + "="*70)
                        log_success("BOT REATIVADO - Voltando a processar tokens!")
                        log_info("="*70 + "\n")
                    else:
                        log_warning("\n" + "="*70)
                        log_warning("BOT DESATIVADO - Parando processamento de novos tokens")
                        log_warning("   (Tokens já comprados continuam sendo monitorados)")
                        log_warning("   (Para reativar, use a interface web: http://localhost:5000)")
                        log_info("="*70 + "\n")
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Em caso de erro, continua monitorando
                pass
    
    async def start(self):
        """Start the bot"""
        await self.initialize()
        
        # Busca o grupo/canal pelo nome ou ID (para grupos privados)
        target_chat_id = None
        target_chat_name = config.TELEGRAM_CHANNEL
        
        try:
            log_info(f"🔍 Buscando grupo/canal: {config.TELEGRAM_CHANNEL}")
            
            # Primeiro, tenta usar diretamente se for um número (ID)
            try:
                if config.TELEGRAM_CHANNEL.lstrip('-').isdigit():
                    target_chat_id = int(config.TELEGRAM_CHANNEL)
                    target_chat = await self.client.get_entity(target_chat_id)
                    target_chat_name = target_chat.title if hasattr(target_chat, 'title') else str(target_chat_id)
                    log_success(f"Grupo encontrado por ID: {target_chat_name} (ID: {target_chat_id})")
                else:
                    # Se não for número, busca pelo nome nos diálogos
                    async for dialog in self.client.iter_dialogs():
                        if dialog.name.lower() == config.TELEGRAM_CHANNEL.lower() or dialog.name == config.TELEGRAM_CHANNEL:
                            target_chat_id = dialog.id
                            target_chat_name = dialog.name
                            log_success(f"Grupo encontrado: {dialog.name} (ID: {dialog.id})")
                            break
                    
                    if not target_chat_id:
                        # Tenta buscar por username (se tiver @)
                        if config.TELEGRAM_CHANNEL.startswith('@'):
                            target_chat = await self.client.get_entity(config.TELEGRAM_CHANNEL)
                            target_chat_id = target_chat.id
                            target_chat_name = target_chat.title if hasattr(target_chat, 'title') else config.TELEGRAM_CHANNEL
                            log_success(f"Grupo encontrado por username: {target_chat_name} (ID: {target_chat_id})")
            except Exception as e:
                log_warning(f"Erro ao buscar: {e}")
                # Se falhar, tenta buscar nos diálogos novamente
                pass
            
            if not target_chat_id:
                log_error(f"Não foi possível encontrar o grupo/canal: {config.TELEGRAM_CHANNEL}")
                log_info("\n   Grupos disponíveis:")
                log_info("   " + "-"*66)
                count = 0
                async for dialog in self.client.iter_dialogs():
                    if (dialog.is_group or dialog.is_channel) and count < 10:
                        log_info(f"   - {dialog.name} (ID: {dialog.id})")
                        count += 1
                log_info("   " + "-"*66)
                log_info("\n   💡 Execute: python descobrir_grupo.py")
                log_info("   Para ver todos os grupos e encontrar o ID correto")
                raise Exception(f"Grupo '{config.TELEGRAM_CHANNEL}' não encontrado")
        except Exception as e:
            log_error(f"Erro ao buscar grupo: {e}")
            raise
        
        # Register event handler usando o ID do grupo
        @self.client.on(events.NewMessage(chats=target_chat_id))
        async def handler(event):
            await self.on_new_message(event)
        
        log_info(f"👂 Monitorando canal: {target_chat_name} (ID: {target_chat_id})")
        log_info(f"📊 Score range: {config.MIN_SCORE}-{config.MAX_SCORE}")
        log_info(f"💰 Valores por score:")
        log_info(f"   Score 15-17: {config.AMOUNT_SOL_15_17} SOL - Máx {config.MAX_TIME_MINUTES_15_17}min")
        log_info(f"   Score 18-19: {config.AMOUNT_SOL_18_19} SOL - Máx {config.MAX_TIME_MINUTES_18_19}min")
        log_info(f"   Score 20-21: {config.AMOUNT_SOL_20_21} SOL - Máx {config.MAX_TIME_MINUTES_20_21}min")
        if config.ENABLE_LOW_SCORE:
            log_info(f"   Score <15: {config.AMOUNT_SOL_LOW} SOL")
        log_info("\n⏱️  Regra de Timing: Bot só compra se token foi detectado dentro da janela de tempo!")
        log_info("🤖 Bot ativo! Aguardando novos tokens...\n")
        
        # Monitora estado do bot periodicamente
        self.bot_was_enabled = get_bot_state()
        if self.bot_was_enabled:
            log_success("Bot INICIADO em modo ATIVO")
        else:
            log_warning("Bot INICIADO em modo DESATIVADO")
        
        # Tarefa para monitorar estado
        monitor_task = asyncio.create_task(self._monitor_bot_state())
        
        try:
            # Keep running
            await self.client.run_until_disconnected()
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
    
    async def stop(self):
        """Stop the bot"""
        await self.jupiter.close()
        await self.client.disconnect()

async def main():
    bot = TradingBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        from logger import log_info
        log_info("\n🛑 Parando bot...")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())

