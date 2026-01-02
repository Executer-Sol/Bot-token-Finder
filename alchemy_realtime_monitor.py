"""
Monitor em tempo real usando Alchemy APIs
Atualiza interface automaticamente quando detecta mudanças
"""
import asyncio
import aiohttp
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from alchemy_integration import AlchemyClient

class AlchemyRealtimeMonitor:
    def __init__(self, api_key: str = None):
        self.client = AlchemyClient(api_key)
        self.is_running = False
        self.last_transaction_signature = None
        self.last_balance = None
        self.wallet_address = None
        self.update_callbacks = []
        
    def set_wallet_address(self, wallet_address: str):
        """Define endereço da carteira para monitorar"""
        self.wallet_address = wallet_address
    
    def add_update_callback(self, callback):
        """Adiciona callback para ser chamado quando houver atualizações"""
        self.update_callbacks.append(callback)
    
    async def notify_update(self, update_type: str, data: Dict):
        """Notifica todos os callbacks sobre uma atualização"""
        for callback in self.update_callbacks:
            try:
                await callback(update_type, data)
            except Exception as e:
                print(f"⚠️  Erro ao chamar callback: {e}")
    
    async def monitor_transactions(self, interval: int = 5):
        """Monitora transações em tempo real
        
        Args:
            interval: Intervalo em segundos para verificar novas transações
        """
        if not self.wallet_address:
            print("⚠️  Endereço da carteira não configurado")
            return
        
        if not self.client.is_configured():
            print("⚠️  Alchemy API key não configurada")
            return
        
        print(f"🔄 Iniciando monitoramento de transações para {self.wallet_address[:8]}...")
        
        while self.is_running:
            try:
                # Busca transferências recentes
                transfers = await self.client.get_transfers(self.wallet_address, limit=10)
                
                if transfers and len(transfers) > 0:
                    # Verifica se há nova transação
                    latest_transfer = transfers[0]
                    latest_signature = latest_transfer.get('hash', '')
                    
                    if latest_signature != self.last_transaction_signature:
                        # Nova transação detectada!
                        self.last_transaction_signature = latest_signature
                        
                        # Verifica se é uma venda (recebeu SOL)
                        if (latest_transfer.get('to', '').upper() == self.wallet_address.upper() and
                            latest_transfer.get('value', 0) > 0):
                            
                            await self.notify_update('new_sell', {
                                'signature': latest_signature,
                                'sol_received': latest_transfer.get('value', 0),
                                'token_mint': latest_transfer.get('token_address', ''),
                                'token_symbol': latest_transfer.get('token_symbol', 'UNKNOWN'),
                                'timestamp': latest_transfer.get('block_timestamp', ''),
                                'transfer': latest_transfer
                            })
                            print(f"✅ Nova venda detectada: {latest_transfer.get('token_symbol', 'UNKNOWN')}")
                        
                        # Notifica nova transação
                        await self.notify_update('new_transaction', {
                            'signature': latest_signature,
                            'transfer': latest_transfer
                        })
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"⚠️  Erro no monitoramento: {e}")
                await asyncio.sleep(interval * 2)  # Espera mais tempo em caso de erro
    
    async def monitor_balance(self, interval: int = 10):
        """Monitora saldo da carteira em tempo real
        
        Args:
            interval: Intervalo em segundos para verificar mudanças de saldo
        """
        if not self.wallet_address:
            return
        
        if not self.client.is_configured():
            return
        
        print(f"💰 Iniciando monitoramento de saldo...")
        
        while self.is_running:
            try:
                # Busca portfólio atualizado
                portfolio = await self.client.get_portfolio(self.wallet_address)
                
                if portfolio:
                    current_balance = portfolio.get('sol_balance', 0)
                    total_value = portfolio.get('total_value_usd', 0)
                    
                    # Verifica se houve mudança significativa (> 0.001 SOL)
                    if self.last_balance is not None:
                        balance_change = current_balance - self.last_balance
                        
                        if abs(balance_change) > 0.001:
                            await self.notify_update('balance_change', {
                                'sol_balance': current_balance,
                                'total_value_usd': total_value,
                                'change': balance_change,
                                'tokens': portfolio.get('tokens', [])
                            })
                            print(f"💰 Saldo mudou: {self.last_balance:.4f} → {current_balance:.4f} SOL")
                    
                    self.last_balance = current_balance
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"⚠️  Erro ao monitorar saldo: {e}")
                await asyncio.sleep(interval * 2)
    
    async def monitor_token_prices(self, token_mints: List[str], interval: int = 30):
        """Monitora preços de tokens específicos
        
        Args:
            token_mints: Lista de endereços de tokens para monitorar
            interval: Intervalo em segundos
        """
        if not token_mints:
            return
        
        if not self.client.is_configured():
            return
        
        print(f"📊 Iniciando monitoramento de preços para {len(token_mints)} tokens...")
        
        last_prices = {}
        
        while self.is_running:
            try:
                for mint in token_mints:
                    price = await self.client.get_token_price(mint)
                    
                    if price and price > 0:
                        last_price = last_prices.get(mint)
                        
                        if last_price:
                            change_percent = ((price - last_price) / last_price) * 100
                            
                            # Notifica se mudança significativa (> 5%)
                            if abs(change_percent) > 5:
                                await self.notify_update('price_change', {
                                    'token_mint': mint,
                                    'price': price,
                                    'change_percent': change_percent,
                                    'last_price': last_price
                                })
                        
                        last_prices[mint] = price
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"⚠️  Erro ao monitorar preços: {e}")
                await asyncio.sleep(interval * 2)
    
    async def start(self, wallet_address: str):
        """Inicia monitoramento em tempo real"""
        self.wallet_address = wallet_address
        self.is_running = True
        
        # Inicia todas as tarefas de monitoramento
        tasks = [
            self.monitor_transactions(interval=5),
            self.monitor_balance(interval=10)
        ]
        
        await asyncio.gather(*tasks)
    
    def stop(self):
        """Para o monitoramento"""
        self.is_running = False
        print("⏸️  Monitoramento parado")

# Instância global
_monitor_instance = None

def get_realtime_monitor(api_key: str = None) -> AlchemyRealtimeMonitor:
    """Retorna instância do monitor em tempo real"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = AlchemyRealtimeMonitor(api_key)
    return _monitor_instance

async def start_realtime_monitoring(wallet_address: str, api_key: str = None):
    """Inicia monitoramento em tempo real"""
    monitor = get_realtime_monitor(api_key)
    await monitor.start(wallet_address)

def stop_realtime_monitoring():
    """Para monitoramento em tempo real"""
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop()
        _monitor_instance = None










