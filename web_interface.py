"""
Interface Web para monitorar trades do bot
Acesse: http://localhost:5000
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timezone
from typing import Dict, List
from bot_control import get_bot_state, set_bot_state
from last_token_detected import get_last_token
from wallet_balance import get_wallet_balance_sync
import asyncio

app = Flask(__name__)
CORS(app)

# Arquivo para salvar histórico de trades
TRADES_FILE = 'trades_history.json'

class TradeTracker:
    def __init__(self):
        self.trades_file = TRADES_FILE
        self.load_trades()
    
    def load_trades(self):
        """Carrega histórico de trades do arquivo"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r', encoding='utf-8') as f:
                    self.trades = json.load(f)
            except:
                self.trades = {'active': [], 'sold': []}
        else:
            self.trades = {'active': [], 'sold': []}
    
    def save_trades(self):
        """Salva histórico de trades no arquivo"""
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def add_active_trade(self, symbol: str, ca: str, entry_price: float, 
                        amount_sol: float, score: int, tx: str):
        """Adiciona trade ativo
        Args:
            amount_sol: Quantidade investida em SOL
        """
        trade = {
            'symbol': symbol,
            'contract_address': ca,
            'entry_price': entry_price,
            'amount_sol': amount_sol,  # Agora em SOL
            'score': score,
            'tx': tx,
            'timestamp': datetime.now().isoformat(),
            'current_price': entry_price,
            'multiple': 1.0,
            'percent_change': 0.0,
            'remaining_percent': 100.0,
            'tps_executed': []
        }
        self.trades['active'].append(trade)
        self.save_trades()
        return trade
    
    def update_active_trade(self, ca: str, current_price: float = None, 
                           remaining_percent: float = None, 
                           tps_executed: List = None):
        """Atualiza trade ativo"""
        for trade in self.trades['active']:
            if trade['contract_address'] == ca:
                if current_price is not None:
                    trade['current_price'] = current_price
                    trade['multiple'] = current_price / trade['entry_price']
                    trade['percent_change'] = (trade['multiple'] - 1) * 100
                if remaining_percent is not None:
                    trade['remaining_percent'] = remaining_percent
                if tps_executed is not None:
                    trade['tps_executed'] = tps_executed
                self.save_trades()
                return trade
        return None
    
    def move_to_sold(self, ca: str, final_price: float = None, total_sold_percent: float = 100.0, 
                     reason: str = None, time_to_peak: float = None, time_to_sell: float = None,
                     peak_multiple: float = None):
        """Move trade de ativo para vendido
        Args:
            reason: Motivo da venda (ex: 'stop_loss_time', 'take_profit', etc)
            time_to_peak: Tempo em minutos até atingir o pico
            time_to_sell: Tempo em minutos até vender completamente
            peak_multiple: Maior múltiplo atingido
        """
        for i, trade in enumerate(self.trades['active']):
            if trade['contract_address'] == ca:
                sold_trade = trade.copy()
                sold_trade['final_price'] = final_price or trade['current_price']
                sold_trade['sold_at'] = datetime.now().isoformat()
                sold_trade['total_sold_percent'] = total_sold_percent
                sold_trade['sell_reason'] = reason or 'manual'  # stop_loss_time, take_profit, manual
                
                # Salva informações de tempo
                if time_to_peak is not None:
                    sold_trade['time_to_peak'] = round(time_to_peak, 2)  # minutos
                if time_to_sell is not None:
                    sold_trade['time_to_sell'] = round(time_to_sell, 2)  # minutos
                if peak_multiple is not None:
                    sold_trade['peak_multiple'] = round(peak_multiple, 4)
                
                # Calcula preço médio ponderado se houver vendas parciais
                average_sell_price = final_price
                total_sold_percent_calculated = total_sold_percent
                
                if trade.get('tps_executed') and len(trade['tps_executed']) > 0:
                    # Calcula preço médio ponderado de todas as vendas
                    total_weighted_price = 0.0
                    total_weighted_percent = 0.0
                    
                    # Processa todas as vendas parciais
                    for tp in trade['tps_executed']:
                        if isinstance(tp, dict):
                            tp_percent = tp.get('percent', 0)
                            tp_price = tp.get('price', 0)
                            if tp_percent > 0 and tp_price > 0:
                                total_weighted_price += tp_price * tp_percent
                                total_weighted_percent += tp_percent
                    
                    # Adiciona a venda final (se houver)
                    if final_price and final_price > 0:
                        remaining_to_sell = 100.0 - total_weighted_percent
                        if remaining_to_sell > 0:
                            total_weighted_price += final_price * remaining_to_sell
                            total_weighted_percent += remaining_to_sell
                    
                    # Calcula média ponderada
                    if total_weighted_percent > 0:
                        average_sell_price = total_weighted_price / total_weighted_percent
                        sold_trade['average_sell_price'] = round(average_sell_price, 10)
                        sold_trade['total_sales'] = len(trade['tps_executed']) + 1  # +1 para venda final
                
                # Calcula lucro/perda em SOL usando preço médio
                entry_value_sol = trade.get('amount_sol', trade.get('amount_usdc', 0) / 100.0)
                final_multiple = average_sell_price / trade['entry_price'] if trade['entry_price'] > 0 else 1.0
                final_value_sol = entry_value_sol * final_multiple * (total_sold_percent / 100)
                profit_loss_sol = final_value_sol - (entry_value_sol * (total_sold_percent / 100))
                profit_loss_percent = ((final_multiple - 1) * 100)
                
                # Atualiza final_price com o preço médio para cálculos
                sold_trade['final_price'] = average_sell_price
                
                sold_trade['profit_loss_sol'] = profit_loss_sol
                sold_trade['profit_loss_percent'] = profit_loss_percent
                sold_trade['final_value_sol'] = final_value_sol
                
                self.trades['sold'].append(sold_trade)
                self.trades['active'].pop(i)
                self.save_trades()
                return sold_trade
        return None
    
    def get_stats(self):
        """Retorna estatísticas gerais (em SOL)"""
        from datetime import datetime, date
        
        active = self.trades['active']
        sold = self.trades['sold']
        all_trades = active + sold
        
        # Usa amount_sol (pode ter trades antigos com amount_usdc, usa fallback)
        total_active_value = sum(t.get('amount_sol', t.get('amount_usdc', 0) / 100.0) for t in active)
        total_active_current = sum(
            (t.get('amount_sol', t.get('amount_usdc', 0) / 100.0)) * t['multiple'] * (t['remaining_percent'] / 100) 
            for t in active
        )
        
        # Para trades vendidos, usa profit_loss_sol ou converte de USDC se antigo
        total_sold_profit = sum(t.get('profit_loss_sol', t.get('profit_loss_usdc', 0) / 100.0) for t in sold)
        total_sold_value = sum(t.get('final_value_sol', t.get('final_value_usdc', 0) / 100.0) for t in sold)
        
        # Calcula win rate (trades lucrativos vs total)
        profitable_trades = sum(1 for t in sold if t.get('profit_loss_sol', t.get('profit_loss_usdc', 0) / 100.0) > 0)
        total_sold_with_result = len([t for t in sold if 'profit_loss_sol' in t or 'profit_loss_usdc' in t])
        win_rate = (profitable_trades / total_sold_with_result * 100) if total_sold_with_result > 0 else 0
        
        # ROI médio (apenas trades vendidos)
        avg_roi = (total_sold_profit / total_sold_value * 100) if total_sold_value > 0 else 0
        
        # Estatísticas do dia
        today = date.today().isoformat()
        today_trades = [t for t in all_trades if t.get('timestamp', '').startswith(today)]
        today_count = len(today_trades)
        
        # Lucros/perdas do dia (ativos + vendidos)
        today_active_profit = sum(
            (t.get('amount_sol', t.get('amount_usdc', 0) / 100.0)) * (t['multiple'] - 1) * (t.get('remaining_percent', 100) / 100)
            for t in today_trades if t in active
        )
        today_sold_profit = sum(
            t.get('profit_loss_sol', t.get('profit_loss_usdc', 0) / 100.0)
            for t in today_trades if t in sold
        )
        today_total_profit = today_active_profit + today_sold_profit
        
        # Total de tokens comprados (histórico)
        total_tokens_bought = len(all_trades)
        
        # Análise por score (apenas vendidos) - agrupa em ranges
        score_analysis = {}
        for trade in sold:
            score = trade.get('score', 0)
            profit = trade.get('profit_loss_sol', trade.get('profit_loss_usdc', 0) / 100.0)
            entry_value = trade.get('amount_sol', trade.get('amount_usdc', 0) / 100.0)
            
            # Agrupa por range de score
            if 15 <= score <= 17:
                score_range = '15-17'
            elif 18 <= score <= 19:
                score_range = '18-19'
            elif 20 <= score <= 21:
                score_range = '20-21'
            elif score < 15:
                score_range = '<15'
            else:
                score_range = 'other'
            
            if score_range not in score_analysis:
                score_analysis[score_range] = {
                    'count': 0, 
                    'profitable': 0, 
                    'total_profit': 0.0,
                    'total_invested': 0.0,
                    'total_return': 0.0
                }
            
            score_analysis[score_range]['count'] += 1
            score_analysis[score_range]['total_profit'] += profit
            score_analysis[score_range]['total_invested'] += entry_value
            score_analysis[score_range]['total_return'] += (entry_value + profit)
            
            if profit > 0:
                score_analysis[score_range]['profitable'] += 1
        
        # Calcula ROI médio e win rate por range
        for score_range, data in score_analysis.items():
            if data['count'] > 0:
                data['win_rate'] = (data['profitable'] / data['count'] * 100) if data['count'] > 0 else 0
                data['avg_roi'] = ((data['total_profit'] / data['total_invested'] * 100) if data['total_invested'] > 0 else 0)
            else:
                data['win_rate'] = 0
                data['avg_roi'] = 0
        
        # Análise de tokens ativos (lucro/perda atual)
        active_analysis = []
        for trade in active:
            amount = trade.get('amount_sol', trade.get('amount_usdc', 0) / 100.0)
            current_value = amount * trade['multiple'] * (trade.get('remaining_percent', 100) / 100)
            profit_loss = current_value - amount
            active_analysis.append({
                'symbol': trade['symbol'],
                'score': trade.get('score', 0),
                'profit_loss': profit_loss,
                'percent': trade.get('percent_change', 0),
                'multiple': trade.get('multiple', 1.0)
            })
        
        # Análise de performance com métricas de tempo (apenas tokens vendidos)
        performance_analysis = {
            'best_tokens': [],
            'worst_tokens': [],
            'avg_time_to_peak': None,
            'avg_time_to_sell': None,
            'avg_peak_multiple': None,
            'tokens_with_peak_data': 0,
            'tokens_with_sell_data': 0
        }
        
        if len(sold) > 0:
            # Tokens com dados de tempo
            tokens_with_peak = [t for t in sold if 'time_to_peak' in t and t['time_to_peak'] is not None]
            tokens_with_sell = [t for t in sold if 'time_to_sell' in t and t['time_to_sell'] is not None]
            tokens_with_peak_mult = [t for t in sold if 'peak_multiple' in t and t['peak_multiple'] is not None]
            
            performance_analysis['tokens_with_peak_data'] = len(tokens_with_peak)
            performance_analysis['tokens_with_sell_data'] = len(tokens_with_sell)
            
            # Calcula médias
            if tokens_with_peak:
                performance_analysis['avg_time_to_peak'] = round(
                    sum(t['time_to_peak'] for t in tokens_with_peak) / len(tokens_with_peak), 2
                )
            
            if tokens_with_sell:
                performance_analysis['avg_time_to_sell'] = round(
                    sum(t['time_to_sell'] for t in tokens_with_sell) / len(tokens_with_sell), 2
                )
            
            if tokens_with_peak_mult:
                performance_analysis['avg_peak_multiple'] = round(
                    sum(t['peak_multiple'] for t in tokens_with_peak_mult) / len(tokens_with_peak_mult), 4
                )
            
            # Melhores e piores tokens (por lucro/perda)
            sorted_by_profit = sorted(
                sold, 
                key=lambda t: t.get('profit_loss_sol', t.get('profit_loss_usdc', 0) / 100.0),
                reverse=True
            )
            
            # Top 5 melhores
            performance_analysis['best_tokens'] = [
                {
                    'symbol': t['symbol'],
                    'score': t.get('score', 0),
                    'profit_loss': round(t.get('profit_loss_sol', t.get('profit_loss_usdc', 0) / 100.0), 4),
                    'time_to_peak': t.get('time_to_peak'),
                    'time_to_sell': t.get('time_to_sell'),
                    'peak_multiple': t.get('peak_multiple'),
                    'final_multiple': round(t.get('final_price', 0) / t.get('entry_price', 1), 4) if t.get('entry_price') else None
                }
                for t in sorted_by_profit[:5]
            ]
            
            # Top 5 piores
            performance_analysis['worst_tokens'] = [
                {
                    'symbol': t['symbol'],
                    'score': t.get('score', 0),
                    'profit_loss': round(t.get('profit_loss_sol', t.get('profit_loss_usdc', 0) / 100.0), 4),
                    'time_to_peak': t.get('time_to_peak'),
                    'time_to_sell': t.get('time_to_sell'),
                    'peak_multiple': t.get('peak_multiple'),
                    'final_multiple': round(t.get('final_price', 0) / t.get('entry_price', 1), 4) if t.get('entry_price') else None
                }
                for t in sorted_by_profit[-5:]
            ]
        
        return {
            'active_count': len(active),
            'sold_count': len(sold),
            'total_active_invested': total_active_value,
            'total_active_current': total_active_current,
            'total_active_profit_loss': total_active_current - total_active_value,
            'total_sold_profit_loss': total_sold_profit,
            'total_sold_value': total_sold_value,
            'overall_profit_loss': (total_active_current - total_active_value) + total_sold_profit,
            'win_rate': round(win_rate, 2),
            'avg_roi': round(avg_roi, 2),
            'profitable_trades': profitable_trades,
            'losing_trades': total_sold_with_result - profitable_trades,
            # Novas estatísticas
            'today_tokens_bought': today_count,
            'total_tokens_bought': total_tokens_bought,
            'today_profit': round(today_total_profit, 4),
            'score_analysis': score_analysis,
            'active_analysis': active_analysis,
            'performance_analysis': performance_analysis
        }

# Instância global do tracker
tracker = TradeTracker()

@app.route('/')
def index():
    """Página principal"""
    return render_template('dashboard.html')

@app.route('/favicon.ico')
def favicon():
    """Retorna 204 para evitar logs de 404"""
    return '', 204

@app.route('/api/trades/active')
def get_active_trades():
    """Retorna trades ativos"""
    tracker.load_trades()  # Recarrega do arquivo para ter dados atualizados
    return jsonify(tracker.trades['active'])

@app.route('/api/trades/active/update-prices', methods=['POST'])
def update_active_trades_prices():
    """Atualiza preços de todos os trades ativos"""
    try:
        from price_monitor import PriceMonitor
        import asyncio
        
        tracker.load_trades()
        active_trades = tracker.trades.get('active', [])
        
        monitor = PriceMonitor()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        updated_count = 0
        try:
            for trade in active_trades:
                ca = trade.get('contract_address')
                if not ca:
                    continue
                
                try:
                    # Busca preço atual
                    current_price = loop.run_until_complete(monitor.get_token_price(ca))
                    
                    if current_price and current_price > 0:
                        # Atualiza trade com novo preço
                        tracker.update_active_trade(ca, current_price=current_price)
                        updated_count += 1
                except Exception as e:
                    # Continua com próximo trade se falhar
                    continue
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'updated': updated_count,
            'total': len(active_trades),
            'message': f'{updated_count} de {len(active_trades)} preços atualizados'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/trades/sold')
def get_sold_trades():
    """Retorna trades vendidos"""
    tracker.load_trades()  # Recarrega do arquivo para ter dados atualizados
    return jsonify(tracker.trades['sold'])

@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas"""
    tracker.load_trades()  # Recarrega do arquivo para ter dados atualizados
    return jsonify(tracker.get_stats())

@app.route('/api/trades/all')
def get_all_trades():
    """Retorna todos os trades"""
    return jsonify(tracker.trades)

@app.route('/api/reset-all', methods=['POST'])
def reset_all_data():
    """Reseta todos os dados (trades ativos e vendidos)"""
    try:
        # Cria backup antes de resetar
        backup_file = f'trades_history_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        if os.path.exists(TRADES_FILE):
            import shutil
            shutil.copy2(TRADES_FILE, backup_file)
            print(f"📦 Backup criado: {backup_file}")
        
        # Reseta os dados
        tracker.trades = {'active': [], 'sold': []}
        tracker.save_trades()
        
        # Reseta limite diário também
        try:
            from daily_loss_limit import reset_daily_stats
            reset_daily_stats()
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Todos os dados foram resetados',
            'backup': backup_file if os.path.exists(backup_file) else None
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Erro ao resetar dados: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/mark-sold', methods=['POST'])
def mark_trade_sold():
    """Marca um trade como vendido manualmente"""
    try:
        data = request.json
        ca = data.get('contract_address', '').strip()
        final_price = data.get('final_price')
        total_sold_percent = float(data.get('total_sold_percent', 100.0))
        
        if not ca:
            return jsonify({'error': 'Contract address não fornecido'}), 400
        
        if final_price is None or final_price <= 0:
            return jsonify({'error': 'Preço de venda inválido'}), 400
        
        if total_sold_percent <= 0 or total_sold_percent > 100:
            return jsonify({'error': 'Porcentagem de venda inválida (deve ser entre 1 e 100)'}), 400
        
        # Busca o trade ativo
        trade = None
        for t in tracker.trades['active']:
            if t['contract_address'] == ca:
                trade = t
                break
        
        if not trade:
            return jsonify({'error': 'Token ativo não encontrado'}), 404
        
        # Calcula tempo desde a compra até agora (para venda manual)
        from datetime import datetime, timezone
        try:
            # Tenta parsear o timestamp (pode estar em diferentes formatos)
            timestamp_str = trade['timestamp']
            if 'T' in timestamp_str:
                # Formato ISO com ou sem Z
                if timestamp_str.endswith('Z'):
                    bought_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                elif '+' in timestamp_str or timestamp_str.count('-') > 2:
                    # Tem timezone
                    bought_at = datetime.fromisoformat(timestamp_str)
                else:
                    # Sem timezone, adiciona UTC
                    bought_at = datetime.fromisoformat(timestamp_str)
                    if bought_at.tzinfo is None:
                        bought_at = bought_at.replace(tzinfo=timezone.utc)
            else:
                # Formato antigo, tenta parsear
                bought_at = datetime.fromisoformat(timestamp_str)
                if bought_at.tzinfo is None:
                    bought_at = bought_at.replace(tzinfo=timezone.utc)
        except Exception as e:
            # Se falhar, usa timestamp atual (fallback)
            print(f"⚠️ Erro ao parsear timestamp {trade['timestamp']}: {e}")
            bought_at = datetime.now(timezone.utc)
        
        sold_at = datetime.now(timezone.utc)
        time_to_sell = (sold_at - bought_at).total_seconds() / 60  # minutos
        
        # Para venda manual, não temos dados de pico histórico
        # Usa o múltiplo atual como referência (pode não ser o pico real)
        time_to_peak = None
        peak_multiple = trade.get('max_multiple_reached', trade.get('multiple', 1.0))
        
        # Se o múltiplo atual é maior que 1.0, considera que já subiu
        # Mas não temos o tempo exato do pico, então deixa como None
        
        # Verifica se é venda parcial ou total
        remaining_percent = trade.get('remaining_percent', 100.0)
        actual_sell_percent = min(total_sold_percent, remaining_percent)
        
        # Cria objeto completo da venda manual
        manual_sale_info = {
            'type': 'manual_partial_sell',
            'percent': actual_sell_percent,
            'price': final_price,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'tx': None  # Venda manual via interface não tem TX (apenas marcação)
        }
        
        # Se vender tudo que resta (ou mais), marca como vendido completamente
        if actual_sell_percent >= remaining_percent:
            # Adiciona a venda manual ao histórico antes de mover
            trade['tps_executed'] = trade.get('tps_executed', []) + [manual_sale_info]
            
            # Marca como vendido completamente
            sold_trade = tracker.move_to_sold(
                ca,
                final_price=final_price,
                total_sold_percent=remaining_percent,  # Vende apenas o que resta
                reason='manual',
                time_to_peak=time_to_peak,
                time_to_sell=time_to_sell,
                peak_multiple=peak_multiple
            )
        else:
            # Venda parcial - atualiza o trade ativo E cria entrada na aba vendidos
            new_remaining = remaining_percent - actual_sell_percent
            
            # Atualiza trade ativo com novo remaining_percent
            tracker.update_active_trade(
                ca,
                remaining_percent=new_remaining,
                tps_executed=trade.get('tps_executed', []) + [manual_sale_info]
            )
            
            # IMPORTANTE: Cria uma entrada na aba vendidos para venda parcial também
            # Isso permite que o usuário veja todas as vendas, mesmo parciais
            partial_sold_trade = trade.copy()
            partial_sold_trade['final_price'] = final_price
            partial_sold_trade['sold_at'] = datetime.now(timezone.utc).isoformat()
            partial_sold_trade['total_sold_percent'] = actual_sell_percent
            partial_sold_trade['sell_reason'] = 'manual_partial'
            partial_sold_trade['remaining_percent_after_sale'] = new_remaining
            partial_sold_trade['is_partial_sale'] = True
            partial_sold_trade['original_contract_address'] = ca  # Para identificar que é o mesmo token
            
            # Calcula lucro/perda para esta venda parcial
            entry_value_sol = trade.get('amount_sol', trade.get('amount_usdc', 0) / 100.0)
            final_multiple = final_price / trade['entry_price'] if trade['entry_price'] > 0 else 1.0
            final_value_sol = entry_value_sol * final_multiple * (actual_sell_percent / 100)
            profit_loss_sol = final_value_sol - (entry_value_sol * (actual_sell_percent / 100))
            profit_loss_percent = ((final_multiple - 1) * 100)
            
            partial_sold_trade['profit_loss_sol'] = profit_loss_sol
            partial_sold_trade['profit_loss_percent'] = profit_loss_percent
            partial_sold_trade['final_value_sol'] = final_value_sol
            partial_sold_trade['average_sell_price'] = final_price  # Para venda parcial, é o preço único
            
            # Adiciona à lista de vendidos
            tracker.trades['sold'].append(partial_sold_trade)
            tracker.save_trades()
            
            sold_trade = partial_sold_trade
            
            # Retorna informações da venda parcial
            sold_trade = {
                'symbol': trade['symbol'],
                'contract_address': ca,
                'partial_sale': True,
                'sold_percent': actual_sell_percent,
                'remaining_percent': new_remaining,
                'final_price': final_price,
                'entry_price': trade['entry_price']
            }
        
        if sold_trade:
            # Adiciona ao limite diário (apenas se venda total)
            if not sold_trade.get('partial_sale', False):
                try:
                    from daily_loss_limit import add_trade_result
                    profit_loss_sol = sold_trade.get('profit_loss_sol', 0)
                    add_trade_result(profit_loss_sol)
                except:
                    pass
            
            # Mensagem apropriada
            if sold_trade.get('partial_sale', False):
                message = f'Venda parcial de {actual_sell_percent:.1f}% de {sold_trade["symbol"]} realizada. Restam {sold_trade["remaining_percent"]:.1f}%'
            else:
                message = f'Token {sold_trade["symbol"]} marcado como vendido completamente'
            
            return jsonify({
                'success': True,
                'message': message,
                'trade': sold_trade
            })
        else:
            return jsonify({'error': 'Erro ao processar venda'}), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Erro ao marcar token como vendido: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500

@app.route('/api/bot/state', methods=['GET'])
def get_bot_control_state():
    """Retorna estado do bot (ativado/desativado)"""
    return jsonify({'enabled': get_bot_state()})

@app.route('/api/bot/toggle', methods=['POST'])
def toggle_bot():
    """Ativa/desativa o bot"""
    data = request.json
    enabled = data.get('enabled', True)
    set_bot_state(enabled)
    return jsonify({'enabled': get_bot_state(), 'message': 'Bot ' + ('ativado' if enabled else 'desativado') + ' com sucesso!'})

@app.route('/api/last-token')
def get_last_token_detected():
    """Retorna último token detectado"""
    last_token = get_last_token()
    return jsonify(last_token if last_token else {})

@app.route('/api/detected-tokens', methods=['GET'])
def get_detected_tokens():
    """Retorna lista de todos os tokens detectados"""
    try:
        from detected_tokens_tracker import get_all_detected_tokens
        limit = request.args.get('limit', 100, type=int)
        tokens = get_all_detected_tokens(limit=limit)
        return jsonify({'tokens': tokens})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc(), 'tokens': []}), 500

@app.route('/api/intelligence', methods=['GET'])
def get_intelligence_data():
    """Retorna análise inteligente de tokens detectados"""
    try:
        from intelligence_analyzer import get_intelligence_data
        data = get_intelligence_data()
        return jsonify(data)
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'enough_data': False
        }), 500

@app.route('/api/detected-tokens/<ca>/update-price', methods=['POST'])
def update_detected_token_price(ca):
    """Atualiza preço atual de um token detectado (busca preço automaticamente)"""
    try:
        # Validação: ignora tokens de teste ou endereços inválidos
        if ca.startswith('CA_TEST') or len(ca) < 32 or not ca.replace('_', '').isalnum():
            return jsonify({
                'success': False,
                'error': 'Token de teste ou endereço inválido',
                'skip': True  # Flag para o frontend ignorar silenciosamente
            }), 200  # Retorna 200 para não aparecer como erro no console
        
        from detected_tokens_tracker import update_token_price
        import asyncio
        from price_monitor import PriceMonitor
        
        # Busca preço atual automaticamente
        monitor = PriceMonitor()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            current_price = loop.run_until_complete(monitor.get_token_price(ca))
        finally:
            loop.close()
        
        if current_price and current_price > 0:
            token = update_token_price(ca, current_price)
            if token:
                return jsonify({'success': True, 'token': token, 'price': current_price})
            else:
                return jsonify({
                    'success': False,
                    'error': 'Token não encontrado no histórico',
                    'skip': True
                }), 200  # 200 para não aparecer como erro
        else:
            # Preço não encontrado - pode ser token muito novo ou inválido
            return jsonify({
                'success': False,
                'error': 'Preço não disponível (token pode ser muito novo ou inválido)',
                'skip': True
            }), 200  # 200 para não aparecer como erro
    except Exception as e:
        import traceback
        # Log do erro no servidor, mas retorna resposta amigável
        print(f"⚠️ Erro ao atualizar preço de {ca}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar preço',
            'skip': True
        }), 200  # 200 para não aparecer como erro no console

@app.route('/api/wallet-balance')
def get_wallet_balance_api():
    """Retorna saldos da carteira"""
    try:
        balance = get_wallet_balance_sync()
        return jsonify(balance)
    except Exception as e:
        return jsonify({
            'sol': 0.0,
            'usdc': 0.0,
            'wallet_address': 'Erro',
            'error': str(e)
        })

@app.route('/api/daily-stats', methods=['GET'])
def get_daily_stats_api():
    """Retorna estatísticas do dia"""
    try:
        from daily_loss_limit import get_daily_stats as get_daily_loss_stats
        stats = get_daily_loss_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blacklist', methods=['GET'])
def get_blacklist():
    """Retorna lista de tokens na blacklist"""
    try:
        from token_blacklist import load_blacklist
        blacklist = list(load_blacklist())
        return jsonify({'addresses': blacklist})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blacklist', methods=['POST'])
def add_to_blacklist_api():
    """Adiciona token à blacklist"""
    try:
        from token_blacklist import add_to_blacklist, refresh_blacklist_cache
        data = request.json
        ca = data.get('contract_address', '').strip()
        if not ca:
            return jsonify({'error': 'Contract address não fornecido'}), 400
        add_to_blacklist(ca)
        refresh_blacklist_cache()
        return jsonify({'success': True, 'message': f'Token {ca} adicionado à blacklist'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blacklist/<address>', methods=['DELETE'])
def remove_from_blacklist_api(address):
    """Remove token da blacklist"""
    try:
        from token_blacklist import remove_from_blacklist, refresh_blacklist_cache
        remove_from_blacklist(address)
        refresh_blacklist_cache()
        return jsonify({'success': True, 'message': f'Token {address} removido da blacklist'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manual-buy', methods=['POST'])
def manual_buy_token():
    """Compra manual de token via CA - COMPRA REAL NA BLOCKCHAIN"""
    try:
        data = request.json
        contract_address = data.get('contract_address', '').strip()
        amount_sol = float(data.get('amount_sol', 0))
        
        if not contract_address:
            return jsonify({'success': False, 'error': 'Contract Address não informado'}), 400
        
        if amount_sol <= 0:
            return jsonify({'success': False, 'error': 'Quantidade em SOL inválida'}), 400
        
        # Importa aqui para evitar import circular
        from jupiter_client import JupiterClient
        from price_monitor import PriceMonitor
        import asyncio
        
        async def execute_buy():
            jupiter = JupiterClient()
            try:
                # Compra real na blockchain
                tx_signature, quote = await jupiter.buy_token(contract_address, amount_sol)
                
                # Obtém valores reais
                amount_tokens = int(quote.get('outAmount', 0))
                real_amount_sol = quote.get('real_in_amount_sol', amount_sol)
                
                # Busca preço atual do token para salvar no histórico
                monitor = PriceMonitor()
                current_price = await monitor.get_token_price(contract_address)
                entry_price = current_price if current_price and current_price > 0 else 0.0001
                
                # Salva no histórico (como o bot faz)
                from trade_tracker_integration import log_trade_bought
                log_trade_bought(
                    symbol=contract_address[:8],  # Usa primeiros 8 chars como símbolo
                    ca=contract_address,
                    entry_price=entry_price,
                    amount_sol=real_amount_sol,
                    score=0,  # Score 0 para compras manuais
                    tx=tx_signature,
                    amount_tokens=amount_tokens
                )
                
                await jupiter.close()
                return {
                    'success': True,
                    'tx_signature': tx_signature,
                    'amount_tokens': amount_tokens,
                    'amount_sol': real_amount_sol,
                    'entry_price': entry_price
                }
            except Exception as e:
                await jupiter.close()
                raise e
        
        result = asyncio.run(execute_buy())
        
        if result['success']:
            return jsonify({
                'success': True,
                'tx_signature': result['tx_signature'],
                'amount_tokens': result.get('amount_tokens', 0),
                'amount_sol': result.get('amount_sol', amount_sol),
                'entry_price': result.get('entry_price', 0),
                'message': f'Compra de {result.get("amount_sol", amount_sol):.6f} SOL realizada com sucesso! TX: {result["tx_signature"]}'
            })
        else:
            return jsonify({'success': False, 'error': 'Erro ao executar compra'}), 500
            
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/manual-sell', methods=['POST'])
def manual_sell_token():
    """Venda manual de token via CA - VENDE REAL NA BLOCKCHAIN"""
    try:
        data = request.json
        contract_address = data.get('contract_address', '').strip()
        sell_percent = float(data.get('sell_percent', 100.0))  # Porcentagem a vender (1-100)
        
        if not contract_address:
            return jsonify({'success': False, 'error': 'Contract Address não informado'}), 400
        
        if sell_percent <= 0 or sell_percent > 100:
            return jsonify({'success': False, 'error': 'Porcentagem inválida (deve ser entre 1 e 100)'}), 400
        
        # Busca trade ativo para obter quantidade de tokens
        tracker.load_trades()
        trade = None
        for t in tracker.trades['active']:
            if t['contract_address'] == contract_address:
                trade = t
                break
        
        if not trade:
            return jsonify({'success': False, 'error': 'Token não encontrado nos trades ativos'}), 404
        
        # Importa aqui para evitar import circular
        from jupiter_client import JupiterClient
        from solana.rpc.async_api import AsyncClient
        from solders.keypair import Keypair
        import base58
        import config
        import asyncio
        
        async def execute_sell():
            # Conecta à blockchain para obter saldo de tokens
            client = AsyncClient(config.RPC_URL)
            keypair = Keypair.from_base58_string(config.SOLANA_PRIVATE_KEY)
            
            try:
                # Obtém saldo de tokens da carteira
                from spl.token.async_client import AsyncToken
                from spl.token.constants import TOKEN_PROGRAM_ID
                
                # Busca contas de token do usuário
                token_accounts = await client.get_token_accounts_by_owner(
                    keypair.pubkey(),
                    {"mint": contract_address},
                    commitment="confirmed"
                )
                
                if not token_accounts.value:
                    raise Exception(f"Nenhum token encontrado na carteira para {contract_address}")
                
                # Pega a primeira conta de token (geralmente é a única)
                token_account = token_accounts.value[0]
                account_info = await client.get_account_info(token_account.pubkey, commitment="confirmed")
                
                if not account_info.value:
                    raise Exception("Conta de token não encontrada")
                
                # Decodifica dados da conta para obter saldo
                from spl.token.core import Account
                account_data = Account.decode(account_info.value.data)
                current_balance = account_data.amount
                
                # Calcula quantidade a vender
                amount_to_sell = int((current_balance * sell_percent) / 100)
                
                if amount_to_sell <= 0:
                    raise Exception("Quantidade a vender é zero ou negativa")
                
                # Vende usando Jupiter
                jupiter = JupiterClient()
                try:
                    tx_signature, quote = await jupiter.sell_token(
                        contract_address,
                        amount_to_sell
                    )
                    
                    # Obtém valores reais
                    real_sol_received = quote.get('real_out_amount_sol', 0)
                    tokens_sold = quote.get('real_in_amount_tokens', amount_to_sell)
                    sell_price = quote.get('calculated_price', 0)
                    
                    # Calcula novo saldo restante
                    remaining_tokens = current_balance - tokens_sold
                    remaining_percent = (remaining_tokens / current_balance * 100) if current_balance > 0 else 0
                    
                    # Atualiza trade no histórico
                    from trade_tracker_integration import log_trade_update, log_trade_sold
                    
                    if remaining_percent <= 0.1:  # Vendeu tudo (ou quase tudo)
                        # Marca como vendido completamente
                        log_trade_sold(
                            ca=contract_address,
                            final_price=sell_price if sell_price > 0 else trade.get('current_price', trade.get('entry_price', 0)),
                            total_sold_percent=100.0,
                            reason='manual',
                            real_sol_received=real_sol_received
                        )
                    else:
                        # Venda parcial - atualiza trade
                        new_remaining_percent = remaining_percent
                        
                        # Cria objeto completo da venda manual
                        manual_sale_info = {
                            'type': 'manual_sell',
                            'percent': (tokens_sold / current_balance * 100) if current_balance > 0 else sell_percent,
                            'price': sell_price if sell_price > 0 else trade.get('current_price', trade.get('entry_price', 0)),
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                            'tx': tx_signature,
                            'sol_received': real_sol_received
                        }
                        
                        log_trade_update(
                            ca=contract_address,
                            current_price=sell_price if sell_price > 0 else trade.get('current_price', 0),
                            remaining_percent=new_remaining_percent,
                            tps_executed=trade.get('tps_executed', []) + [manual_sale_info]
                        )
                    
                    await jupiter.close()
                    await client.close()
                    
                    return {
                        'success': True,
                        'tx_signature': tx_signature,
                        'tokens_sold': tokens_sold,
                        'sol_received': real_sol_received,
                        'sell_price': sell_price,
                        'remaining_percent': remaining_percent,
                        'is_full_sale': remaining_percent <= 0.1
                    }
                except Exception as e:
                    await jupiter.close()
                    raise e
            except Exception as e:
                await client.close()
                raise e
        
        result = asyncio.run(execute_sell())
        
        if result['success']:
            message = f"Venda de {result['tokens_sold']} tokens realizada! Recebido: {result['sol_received']:.6f} SOL"
            if result['is_full_sale']:
                message += " (venda completa)"
            else:
                message += f" (restam {result['remaining_percent']:.1f}%)"
            
            return jsonify({
                'success': True,
                'tx_signature': result['tx_signature'],
                'tokens_sold': result['tokens_sold'],
                'sol_received': result['sol_received'],
                'sell_price': result['sell_price'],
                'remaining_percent': result['remaining_percent'],
                'is_full_sale': result['is_full_sale'],
                'message': message
            })
        else:
            return jsonify({'success': False, 'error': 'Erro ao executar venda'}), 500
            
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/trading-config', methods=['GET'])
def get_trading_config():
    """Retorna configurações de trading (TP e Stop Loss)"""
    try:
        from trading_config import load_config
        config = load_config()
        return jsonify(config)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/trading-config', methods=['POST'])
def update_trading_config():
    """Atualiza configurações de trading (TP e Stop Loss)"""
    try:
        from trading_config import load_config, save_config
        data = request.json
        
        config = load_config()
        
        # Atualiza take profits se fornecido
        if 'take_profits' in data:
            config['take_profits'] = data['take_profits']
        
        # Atualiza stop loss se fornecido
        if 'stop_loss' in data:
            config['stop_loss'] = {**config.get('stop_loss', {}), **data['stop_loss']}
        
        save_config(config)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/buy-config', methods=['GET'])
def get_buy_config():
    """Retorna configurações de valores de compra por score"""
    try:
        import config
        return jsonify({
            'buy_amounts': {
                'amount_sol_15_17': config.AMOUNT_SOL_15_17,
                'amount_sol_18_19': config.AMOUNT_SOL_18_19,
                'amount_sol_20_21': config.AMOUNT_SOL_20_21,
                'amount_sol_low': config.AMOUNT_SOL_LOW,
                'enable_low_score': config.ENABLE_LOW_SCORE
            },
            'max_times': {
                'max_time_minutes_15_17': config.MAX_TIME_MINUTES_15_17,
                'max_time_minutes_18_19': config.MAX_TIME_MINUTES_18_19,
                'max_time_minutes_20_21': config.MAX_TIME_MINUTES_20_21
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/buy-config', methods=['POST'])
def update_buy_config():
    """Atualiza configurações de valores de compra por score"""
    try:
        import config
        import os
        
        data = request.json
        env_file = '.env'
        
        # Lê .env atual
        env_vars = {}
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Atualiza valores de compra
        if 'buy_amounts' in data:
            amounts = data['buy_amounts']
            if 'amount_sol_15_17' in amounts:
                env_vars['AMOUNT_SOL_15_17'] = str(amounts['amount_sol_15_17'])
                config.AMOUNT_SOL_15_17 = float(amounts['amount_sol_15_17'])
            if 'amount_sol_18_19' in amounts:
                env_vars['AMOUNT_SOL_18_19'] = str(amounts['amount_sol_18_19'])
                config.AMOUNT_SOL_18_19 = float(amounts['amount_sol_18_19'])
            if 'amount_sol_20_21' in amounts:
                env_vars['AMOUNT_SOL_20_21'] = str(amounts['amount_sol_20_21'])
                config.AMOUNT_SOL_20_21 = float(amounts['amount_sol_20_21'])
            if 'amount_sol_low' in amounts:
                env_vars['AMOUNT_SOL_LOW'] = str(amounts['amount_sol_low'])
                config.AMOUNT_SOL_LOW = float(amounts['amount_sol_low'])
            if 'enable_low_score' in amounts:
                env_vars['ENABLE_LOW_SCORE'] = str(amounts['enable_low_score']).lower()
                config.ENABLE_LOW_SCORE = amounts['enable_low_score']
        
        # Atualiza tempos máximos
        if 'max_times' in data:
            times = data['max_times']
            if 'max_time_minutes_15_17' in times:
                env_vars['MAX_TIME_MINUTES_15_17'] = str(times['max_time_minutes_15_17'])
                config.MAX_TIME_MINUTES_15_17 = int(times['max_time_minutes_15_17'])
            if 'max_time_minutes_18_19' in times:
                env_vars['MAX_TIME_MINUTES_18_19'] = str(times['max_time_minutes_18_19'])
                config.MAX_TIME_MINUTES_18_19 = int(times['max_time_minutes_18_19'])
            if 'max_time_minutes_20_21' in times:
                env_vars['MAX_TIME_MINUTES_20_21'] = str(times['max_time_minutes_20_21'])
                config.MAX_TIME_MINUTES_20_21 = int(times['max_time_minutes_20_21'])
        
        # Salva .env
        with open(env_file, 'w', encoding='utf-8') as f:
            for key, value in env_vars.items():
                f.write(f'{key}={value}\n')
        
        # Retorna configuração atualizada
        return jsonify({
            'success': True,
            'config': {
                'buy_amounts': {
                    'amount_sol_15_17': config.AMOUNT_SOL_15_17,
                    'amount_sol_18_19': config.AMOUNT_SOL_18_19,
                    'amount_sol_20_21': config.AMOUNT_SOL_20_21,
                    'amount_sol_low': config.AMOUNT_SOL_LOW,
                    'enable_low_score': config.ENABLE_LOW_SCORE
                },
                'max_times': {
                    'max_time_minutes_15_17': config.MAX_TIME_MINUTES_15_17,
                    'max_time_minutes_18_19': config.MAX_TIME_MINUTES_18_19,
                    'max_time_minutes_20_21': config.MAX_TIME_MINUTES_20_21
                }
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 Interface Web iniciada!")
    print("="*70)
    print("📍 Acesse: http://localhost:5000")
    print("📊 Dashboard com todos os trades em tempo real")
    print("="*70 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=True)

