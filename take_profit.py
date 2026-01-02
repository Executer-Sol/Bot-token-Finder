"""
Gerenciador de Take Profit - monitora preços e executa vendas parciais
"""
import asyncio
from typing import Dict
from datetime import datetime, timezone
from price_monitor import PriceMonitor
from jupiter_client import JupiterClient
import config
from trade_tracker_integration import log_trade_update, log_trade_sold

class TakeProfitManager:
    def __init__(self, jupiter_client: JupiterClient):
        self.jupiter = jupiter_client
        self.price_monitor = PriceMonitor()
        self.positions: Dict[str, dict] = {}  # {contract_address: position_info}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    def add_position(self, contract_address: str, symbol: str, amount_tokens: int, 
                     entry_price: float, score: int):
        """Adiciona uma nova posição para monitoramento"""
        position = {
            'symbol': symbol,
            'amount_tokens': amount_tokens,
            'remaining_amount': amount_tokens,
            'entry_price': entry_price,
            'score': score,
            'tps_executed': [],
            'bought_at': datetime.now(timezone.utc),  # Timestamp da compra
            'max_multiple_reached': 1.0  # Rastreia o maior múltiplo atingido
        }
        self.positions[contract_address] = position
        
        # Inicia tarefa de monitoramento
        task = asyncio.create_task(self._monitor_position(contract_address))
        self.monitoring_tasks[contract_address] = task
    
    async def _monitor_position(self, contract_address: str):
        """Monitora uma posição e executa vendas quando atingir take profits"""
        position = self.positions.get(contract_address)
        if not position:
            return
        
        while contract_address in self.positions:
            try:
                # Busca preço atual
                current_price = await self.price_monitor.get_token_price(contract_address)
                
                if not current_price or current_price <= 0:
                    await asyncio.sleep(10)
                    continue
                
                # Calcula múltiplo (com proteção contra valores inválidos)
                if position['entry_price'] <= 0 or current_price <= 0:
                    await asyncio.sleep(10)
                    continue
                
                # Validação: Se entry_price for muito pequeno (< 1e-8), provavelmente está errado
                # Tenta buscar preço inicial do token detectado como fallback
                if position['entry_price'] < 1e-8:
                    try:
                        from detected_tokens_tracker import get_all_detected_tokens
                        detected_tokens = get_all_detected_tokens(limit=100)
                        for token in detected_tokens:
                            if token.get('contract_address') == contract_address:
                                initial_price = token.get('initial_price', 0)
                                if initial_price > 1e-8:
                                    print(f"🔧 {position['symbol']}: Corrigindo entry price inválido ({position['entry_price']:.10f}) → ${initial_price:.10f}")
                                    position['entry_price'] = initial_price
                                    # Atualiza também no tracker para persistir a correção
                                    try:
                                        from trade_tracker_integration import get_tracker
                                        tracker = get_tracker()
                                        tracker.update_active_trade(contract_address, current_price=current_price)
                                    except:
                                        pass
                                    break
                    except Exception as e:
                        # Silencioso - não queremos spam de erros
                        pass
                
                # Se ainda estiver inválido, pula esta iteração (mas reduz frequência de logs)
                if position['entry_price'] < 1e-8:
                    # Log apenas a cada 10 iterações para não spammar
                    if not hasattr(position, '_invalid_price_log_count'):
                        position['_invalid_price_log_count'] = 0
                    position['_invalid_price_log_count'] += 1
                    if position['_invalid_price_log_count'] % 10 == 1:
                        print(f"⚠️  {position['symbol']}: Entry price ainda inválido após correção. Aguardando...")
                    await asyncio.sleep(10)
                    continue
                
                # Reset contador se preço válido
                if hasattr(position, '_invalid_price_log_count'):
                    del position['_invalid_price_log_count']
                
                multiple = current_price / position['entry_price']
                percent_change = (multiple - 1) * 100
                
                # Proteção: se múltiplo for absurdo (>1000x), provavelmente é erro de preço
                # Tenta corrigir usando preço inicial do token detectado
                if multiple > 1000:
                    # Log apenas a cada 5 iterações para não spammar
                    if not hasattr(position, '_absurd_multiple_log_count'):
                        position['_absurd_multiple_log_count'] = 0
                    position['_absurd_multiple_log_count'] += 1
                    
                    if position['_absurd_multiple_log_count'] % 5 == 1:
                        print(f"⚠️  {position['symbol']}: Múltiplo absurdo ({multiple:.2f}x) - Entry: ${position['entry_price']:.10f}, Current: ${current_price:.10f}")
                        # Tenta corrigir uma vez
                        try:
                            from detected_tokens_tracker import get_all_detected_tokens
                            detected_tokens = get_all_detected_tokens(limit=100)
                            for token in detected_tokens:
                                if token.get('contract_address') == contract_address:
                                    initial_price = token.get('initial_price', 0)
                                    if initial_price > 1e-8 and abs(initial_price - position['entry_price']) > 1e-8:
                                        print(f"🔧 Corrigindo entry price: ${position['entry_price']:.10f} → ${initial_price:.10f}")
                                        position['entry_price'] = initial_price
                                        # Recalcula múltiplo
                                        multiple = current_price / initial_price
                                        if multiple <= 1000:
                                            print(f"✅ Correção aplicada! Novo múltiplo: {multiple:.3f}x")
                                            position['_absurd_multiple_log_count'] = 0  # Reset contador
                                            break
                        except:
                            pass
                    
                    # Se ainda absurdo, ignora
                    if multiple > 1000:
                        await asyncio.sleep(10)
                        continue
                
                # Atualiza maior múltiplo atingido e registra quando atingiu o pico
                if multiple > position['max_multiple_reached']:
                    position['max_multiple_reached'] = multiple
                    # Registra quando atingiu o pico (primeira vez que bateu este recorde)
                    if 'peak_time' not in position:
                        position['peak_time'] = datetime.now(timezone.utc)
                
                # Calcula tempo desde a compra
                time_since_buy = datetime.now(timezone.utc) - position['bought_at']
                minutes_since_buy = time_since_buy.total_seconds() / 60
                
                # Log atualização
                remaining_percent = (position['remaining_amount'] / position['amount_tokens']) * 100
                log_trade_update(
                    contract_address,
                    current_price,
                    remaining_percent,
                    position['tps_executed']
                )
                
                # STOP LOSS POR TEMPO: Se passou X minutos e não subiu significativamente, vende tudo
                # Baseado na média: tokens que dão certo começam a subir em 1-5 minutos
                # Se não subiu em 5 minutos, provavelmente não vai subir
                if minutes_since_buy >= config.STOP_LOSS_TIME_MINUTES:
                    max_reached = position.get('max_multiple_reached', 1.0)
                    
                    # Log para debug (apenas a cada minuto para não poluir)
                    if int(minutes_since_buy) % 1 == 0 and minutes_since_buy < config.STOP_LOSS_TIME_MINUTES + 1:
                        print(f"⏱️  {position['symbol']}: {minutes_since_buy:.1f} min | Múltiplo: {multiple:.3f}x | Máx: {max_reached:.3f}x")
                    
                    # Condição de venda: 
                    # 1. Se nunca subiu acima de 1.1x (nunca teve movimento significativo) OU
                    # 2. Se caiu abaixo do múltiplo mínimo configurado
                    never_moved = max_reached < 1.1  # Nunca subiu acima de 10%
                    below_minimum = multiple < config.STOP_LOSS_MIN_MULTIPLE  # Caiu abaixo do mínimo
                    should_sell = never_moved or below_minimum
                    
                    if should_sell:
                        print(f"\n⏰ STOP LOSS por tempo: {position['symbol']} não subiu em {config.STOP_LOSS_TIME_MINUTES} minutos")
                        print(f"   Tempo desde compra: {minutes_since_buy:.1f} minutos")
                        print(f"   Múltiplo atual: {multiple:.3f}x")
                        print(f"   Máximo atingido: {max_reached:.3f}x")
                        print(f"   Condição: {'Nunca subiu acima de 1.1x' if never_moved else f'Caiu abaixo de {config.STOP_LOSS_MIN_MULTIPLE}x'}")
                        print(f"   Vendendo 100% para evitar perdas maiores...\n")
                        
                        # Calcula tempos antes de vender
                        sold_at = datetime.now(timezone.utc)
                        time_to_sell = (sold_at - position['bought_at']).total_seconds() / 60  # minutos
                        time_to_peak = None
                        if 'peak_time' in position:
                            time_to_peak = (position['peak_time'] - position['bought_at']).total_seconds() / 60  # minutos
                        
                        # Vende tudo
                        await self._execute_stop_loss(
                            contract_address, 
                            position, 
                            current_price,
                            time_to_peak=time_to_peak,
                            time_to_sell=time_to_sell
                        )
                        
                        # Remove da lista
                        if contract_address in self.positions:
                            del self.positions[contract_address]
                        if contract_address in self.monitoring_tasks:
                            del self.monitoring_tasks[contract_address]
                        break
                
                # NOVA ESTRATÉGIA DE TAKE PROFIT:
                # 1. Quando atinge 2x (100%): vende 50% para recuperar investimento (tirar risco)
                # 2. A cada 100% adicional (3x, 4x, 5x...): vende 10% dos tokens restantes
                
                # Verifica take profits escalonados
                await self._check_scaled_take_profits(contract_address, position, multiple, current_price)
                
                # Se vendeu tudo (via Stop Loss), remove da lista
                if position['remaining_amount'] <= 0:
                    # Calcula tempos antes de remover
                    sold_at = datetime.now(timezone.utc)
                    time_to_sell = (sold_at - position['bought_at']).total_seconds() / 60  # minutos
                    time_to_peak = None
                    if 'peak_time' in position:
                        time_to_peak = (position['peak_time'] - position['bought_at']).total_seconds() / 60  # minutos
                    
                    log_trade_sold(
                        contract_address, 
                        current_price, 
                        reason='take_profit',
                        time_to_peak=time_to_peak,
                        time_to_sell=time_to_sell,
                        peak_multiple=position.get('max_multiple_reached', 1.0)
                    )
                    print(f"✅ Posição {position['symbol']} completamente vendida!")
                    
                    del self.positions[contract_address]
                    if contract_address in self.monitoring_tasks:
                        del self.monitoring_tasks[contract_address]
                    break
                
                await asyncio.sleep(10)  # Verifica a cada 10 segundos
                
            except Exception as e:
                print(f"❌ Erro ao monitorar posição {contract_address}: {e}")
                await asyncio.sleep(10)
    
    def _get_take_profits_for_score(self, score: int) -> list:
        """Retorna lista de take profits baseado no score"""
        if 15 <= score <= 17:
            return [
                {'multiple': config.TP1_MULTIPLE, 'percent': config.TP1_SELL_PERCENT},
                {'multiple': config.TP2_MULTIPLE, 'percent': config.TP2_SELL_PERCENT},
                {'multiple': config.TP3_MULTIPLE, 'percent': config.TP3_SELL_PERCENT}
            ]
        elif 18 <= score <= 19:
            return [
                {'multiple': config.TP1_MULTIPLE_18_19, 'percent': config.TP1_SELL_PERCENT_18_19},
                {'multiple': config.TP2_MULTIPLE_18_19, 'percent': config.TP2_SELL_PERCENT_18_19}
            ]
        elif 20 <= score <= 21:
            return [
                {'multiple': config.TP1_MULTIPLE_20_21, 'percent': config.TP1_SELL_PERCENT_20_21},
                {'multiple': config.TP2_MULTIPLE_20_21, 'percent': config.TP2_SELL_PERCENT_20_21}
            ]
        else:
            return []
    
    async def _check_scaled_take_profits(self, contract_address: str, position: dict, 
                                        multiple: float, current_price: float):
        """Verifica e executa take profits escalonados:
        - 2x (100%): vende 50% para recuperar investimento
        - 3x, 4x, 5x... (a cada 100% adicional): vende 10% dos tokens restantes
        """
        # Garante que temos a lista de múltiplos onde já vendemos
        if 'tp_multiples_executed' not in position:
            position['tp_multiples_executed'] = []
        
        executed_multiples = position['tp_multiples_executed']
        
        # 1. Primeira venda: 2x (100% de alta) - vende 50% para recuperar investimento
        if multiple >= 2.0 and 2.0 not in executed_multiples:
            sell_percent = 50.0  # Vende 50% para recuperar o investimento
            await self._execute_scaled_tp(contract_address, position, 2.0, sell_percent, current_price, 'TP1 (2x - Recuperar Risco)')
            executed_multiples.append(2.0)
            return  # Retorna para evitar múltiplas vendas no mesmo ciclo
        
        # 2. Vendas subsequentes: a cada múltiplo inteiro adicional (3x, 4x, 5x...), vende 10% do restante
        # Calcula qual múltiplo inteiro estamos (3, 4, 5, etc)
        integer_multiple = int(multiple)
        
        # Para cada múltiplo de 3x em diante
        for target_multiple in range(3, integer_multiple + 1):
            if target_multiple not in executed_multiples and multiple >= target_multiple:
                # Vende 10% dos tokens RESTANTES (não do total original)
                sell_percent = 10.0
                await self._execute_scaled_tp(contract_address, position, target_multiple, sell_percent, current_price, f'TP{target_multiple-1} ({target_multiple}x - Venda Parcial)')
                executed_multiples.append(target_multiple)
                return  # Retorna para evitar múltiplas vendas no mesmo ciclo
    
    async def _execute_scaled_tp(self, contract_address: str, position: dict, 
                                 multiple_target: float, sell_percent: float, 
                                 current_price: float, tp_description: str):
        """Executa uma venda parcial no sistema escalonado"""
        try:
            if position['remaining_amount'] <= 0:
                return
            
            # Calcula quantidade a vender (percentual dos tokens RESTANTES)
            amount_to_sell = int((position['remaining_amount'] * sell_percent) / 100)
            
            if amount_to_sell <= 0:
                return
            
            # Calcula percentual do total original (para exibição)
            total_percent = (amount_to_sell / position['amount_tokens']) * 100
            
            print(f"\n💰 {tp_description} para {position['symbol']}")
            print(f"   Múltiplo atual: {multiple_target:.2f}x")
            print(f"   Vendendo {sell_percent}% dos tokens restantes ({total_percent:.1f}% do total original)")
            print(f"   Quantidade: {amount_to_sell} tokens")
            
            # Executa venda via Jupiter
            tx_signature, quote = await self.jupiter.sell_token(
                contract_address,
                amount_to_sell
            )
            
            # Obtém valores reais da venda
            real_sol_received = quote.get('real_out_amount_sol', 0)
            # IMPORTANTE: Usa sempre current_price (em dólares) do monitoramento
            # O calculated_price do Jupiter está em SOL/token, não em dólares
            # O current_price já está em dólares e é mais preciso
            sell_price_usd = current_price  # Preço em dólares do monitoramento
            
            print(f"✅ Venda executada! TX: {tx_signature}")
            print(f"   SOL recebido: {real_sol_received:.6f} SOL")
            print(f"   Preço de venda: ${sell_price_usd:.10f}")
            
            # Atualiza posição
            position['remaining_amount'] -= amount_to_sell
            
            # Salva informações completas da venda parcial
            tp_info = {
                'type': 'take_profit',
                'multiple': multiple_target,
                'percent': total_percent,  # Percentual do total original
                'price': sell_price_usd,  # Preço em dólares
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'tx': tx_signature,
                'sol_received': real_sol_received
            }
            position['tps_executed'].append(tp_info)
            
            # Calcula percentual restante
            remaining_percent = (position['remaining_amount'] / position['amount_tokens']) * 100
            
            # Usa preço de venda em dólares
            actual_price = sell_price_usd
            
            # Log venda parcial (mantém compatibilidade com formato antigo)
            tps_for_log = [f'{multiple_target}x']  # Formato antigo para compatibilidade
            log_trade_update(
                contract_address,
                actual_price,
                remaining_percent,
                position['tps_executed']  # Envia formato novo completo
            )
            
            print(f"   Tokens restantes: {position['remaining_amount']} ({remaining_percent:.1f}% do total original)\n")
            
            # Se vendeu tudo, marca como vendido
            if position['remaining_amount'] <= 0:
                time_to_sell = (datetime.now(timezone.utc) - position['bought_at']).total_seconds() / 60
                time_to_peak = None
                if 'peak_time' in position:
                    time_to_peak = (position['peak_time'] - position['bought_at']).total_seconds() / 60
                
                log_trade_sold(
                    contract_address, 
                    actual_price, 
                    total_sold_percent=100.0,
                    reason='take_profit',
                    time_to_peak=time_to_peak,
                    time_to_sell=time_to_sell,
                    peak_multiple=position.get('max_multiple_reached', 1.0)
                )
                print(f"✅ Posição {position['symbol']} completamente vendida via take profit escalonado!\n")
                
        except Exception as e:
            import traceback
            print(f"❌ Erro ao executar take profit escalonado para {position['symbol']}: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
    
    async def _execute_take_profit(self, contract_address: str, position: dict, 
                                    sell_percent: float, tp_id: str, current_price: float):
        """Executa uma venda parcial (método antigo - mantido para compatibilidade)"""
        try:
            # Calcula quantidade a vender
            amount_to_sell = int((position['remaining_amount'] * sell_percent) / 100)
            
            if amount_to_sell <= 0:
                return
            
            print(f"💰 Executando {tp_id} para {position['symbol']}: vendendo {sell_percent}%")
            
            # Executa venda via Jupiter e obtém valores reais
            tx_signature, quote = await self.jupiter.sell_token(
                contract_address,
                amount_to_sell
            )
            
            # Obtém valores reais da venda
            real_sol_received = quote.get('real_out_amount_sol', 0)
            # IMPORTANTE: Usa sempre current_price (em dólares) do monitoramento
            # O calculated_price do Jupiter está em SOL/token, não em dólares
            sell_price_usd = current_price  # Preço em dólares do monitoramento
            
            print(f"✅ {tp_id} executado! TX: {tx_signature}")
            print(f"   SOL recebido: {real_sol_received:.6f} SOL")
            print(f"   Preço de venda: ${sell_price_usd:.10f}")
            
            # Atualiza posição
            position['remaining_amount'] -= amount_to_sell
            
            # Calcula percentual vendido do total original
            total_percent = (amount_to_sell / position['amount_tokens']) * 100
            
            # Salva informações completas da venda parcial (formato novo)
            tp_info = {
                'type': tp_id,
                'percent': total_percent,  # Percentual do total original
                'price': sell_price_usd,  # Preço em dólares
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'tx': tx_signature,
                'sol_received': real_sol_received
            }
            position['tps_executed'].append(tp_info)
            
            # Usa preço de venda em dólares
            actual_price = sell_price_usd
            
            # Log venda parcial com preço real
            log_trade_update(
                contract_address,
                actual_price,  # Preço real da venda
                (position['remaining_amount'] / position['amount_tokens']) * 100,
                position['tps_executed']
            )
            
            # Se vendeu tudo, marca como vendido com preço real
            if position['remaining_amount'] <= 0:
                log_trade_sold(contract_address, actual_price, reason='take_profit')
                print(f"✅ Posição {position['symbol']} completamente vendida!")
                
        except Exception as e:
            print(f"❌ Erro ao executar take profit {tp_id} para {position['symbol']}: {e}")
    
    async def _execute_stop_loss(self, contract_address: str, position: dict, current_price: float,
                                  time_to_peak: float = None, time_to_sell: float = None):
        """Executa stop loss - vende 100% do token"""
        try:
            if position['remaining_amount'] <= 0:
                print(f"⚠️  {position['symbol']} já foi vendido completamente")
                return
            
            print(f"🛑 Executando STOP LOSS para {position['symbol']}: vendendo 100%")
            print(f"   Quantidade restante: {position['remaining_amount']} tokens")
            print(f"   Preço atual: ${current_price}")
            
            # Executa venda de tudo via Jupiter e obtém valores reais
            tx_signature, quote = await self.jupiter.sell_token(
                contract_address,
                position['remaining_amount']
            )
            
            # Obtém valores reais da venda
            real_sol_received = quote.get('real_out_amount_sol', 0)
            # IMPORTANTE: Usa sempre current_price (em dólares) do monitoramento
            # O calculated_price do Jupiter está em SOL/token, não em dólares
            sell_price_usd = current_price  # Preço em dólares do monitoramento
            
            print(f"✅ STOP LOSS executado! TX: {tx_signature}")
            print(f"   SOL recebido: {real_sol_received:.6f} SOL")
            print(f"   Preço de venda: ${sell_price_usd:.10f}")
            
            # Calcula tempos se não foram passados
            if time_to_sell is None:
                sold_at = datetime.now(timezone.utc)
                time_to_sell = (sold_at - position['bought_at']).total_seconds() / 60
            if time_to_peak is None and 'peak_time' in position:
                time_to_peak = (position['peak_time'] - position['bought_at']).total_seconds() / 60
            
            # Usa preço de venda em dólares
            actual_price = sell_price_usd
            
            # Marca como vendido com preço real
            log_trade_sold(
                contract_address, 
                actual_price,  # Preço real da venda
                total_sold_percent=100.0, 
                reason='stop_loss_time',
                time_to_peak=time_to_peak,
                time_to_sell=time_to_sell,
                peak_multiple=position.get('max_multiple_reached', 1.0)
            )
            print(f"✅ Posição {position['symbol']} vendida por STOP LOSS (não subiu em {config.STOP_LOSS_TIME_MINUTES} minutos)")
            
        except Exception as e:
            import traceback
            print(f"❌ Erro ao executar stop loss para {position['symbol']}: {e}")
            print(f"   Traceback: {traceback.format_exc()}")

