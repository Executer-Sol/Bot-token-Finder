"""
Tipos TypeScript/Python para o projeto
"""
from typing import Optional

class TokenInfo:
    def __init__(self, symbol: str, price: float, fdv: str, score: int, contract_address: str, minutes_detected: int = None):
        self.symbol = symbol
        self.price = price
        self.fdv = fdv
        self.score = score
        self.contract_address = contract_address
        self.minutes_detected = minutes_detected  # Tempo desde primeira detecção

