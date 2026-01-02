import re
from typing import Optional

class TokenInfo:
    def __init__(self, symbol: str, price: float, fdv: str, score: int, contract_address: str, minutes_detected: int = None, detected_at = None):
        self.symbol = symbol
        self.price = price
        self.fdv = fdv
        self.score = score
        self.contract_address = contract_address
        self.minutes_detected = minutes_detected  # Tempo desde primeira detecção
        self.detected_at = detected_at  # Horário de detecção (datetime object)

def parse_token_message(message: str) -> Optional[TokenInfo]:
    """
    Parse token information from Telegram message format:
    #SHIRLEY ● $0.0₃82 82K FDV atualmente
    
    Score: 16 (Spent: 3pts | Wallets: 4pts | Old: 5pts | Buys: 4pts)
    
    CA: FipAgs4hHCm5HBrD4rvAP8LGgrm1iWW4qgB1aTAYpump
    """
    try:
        # Extract symbol (after #)
        symbol_match = re.search(r'#(\w+)', message)
        if not symbol_match:
            return None
        symbol = symbol_match.group(1)
        
        # Extract price (format: $0.0₃82 or similar)
        # O formato pode ser: $0.0₃62 (onde ₃ indica zeros após o decimal)
        price_match = re.search(r'\$(\d+\.?\d*[₀₁₂₃₄₅₆₇₈₉]?\d*)', message)
        if not price_match:
            return None
        
        price_str = price_match.group(1)
        # Convert subscript numbers to decimal
        price = parse_price_with_subscript(price_str)
        
        # Extract FDV
        fdv_match = re.search(r'(\d+[KMB]?)\s*FDV', message)
        fdv = fdv_match.group(1) if fdv_match else "0"
        
        # Extract Score
        score_match = re.search(r'Score:\s*(\d+)', message)
        if not score_match:
            return None
        score = int(score_match.group(1))
        
        # Extract Contract Address (CA:)
        # Aceita CA: endereço ou CA: `endereço` (com backticks)
        ca_match = re.search(r'CA:\s*`?([A-Za-z0-9]+)`?', message)
        if not ca_match:
            return None
        contract_address = ca_match.group(1)
        
        # Extract time detected (ex: "Detectado há 5 minutos" ou "Detectado há 8 horas")
        minutes_detected = None
        # Tenta primeiro minutos
        time_match = re.search(r'Detectado há\s+(\d+)\s+minuto', message, re.IGNORECASE)
        if time_match:
            minutes_detected = int(time_match.group(1))
        else:
            # Tenta horas e converte para minutos
            time_match = re.search(r'Detectado há\s+(\d+)\s+hora', message, re.IGNORECASE)
            if time_match:
                hours = int(time_match.group(1))
                minutes_detected = hours * 60  # Converte horas para minutos
        
        return TokenInfo(symbol, price, fdv, score, contract_address, minutes_detected)
    
    except Exception as e:
        print(f"Erro ao parsear mensagem: {e}")
        return None

def parse_price_with_subscript(price_str: str) -> float:
    """
    Convert price string with subscript numbers to float
    Formato: 0.0₃62 significa 0.000062 (3 zeros após o decimal antes do 62)
    """
    # Verifica se tem formato com subscrito indicando zeros
    # Exemplo: 0.0₃62 -> 0.000062
    subscript_map = {
        '₀': 0, '₁': 1, '₂': 2, '₃': 3, '₄': 4,
        '₅': 5, '₆': 6, '₇': 7, '₈': 8, '₉': 9
    }
    
    # Procura padrão: número.subscrito+digitos (ex: 0.0₃62)
    pattern = r'(\d+)\.(\d*)([₀₁₂₃₄₅₆₇₈₉])(\d+)'
    match = re.search(pattern, price_str)
    
    if match:
        # Formato com subscrito indicando zeros
        before_decimal = match.group(1)  # 0
        zeros_before = match.group(2)    # 0
        subscript = match.group(3)       # ₃
        digits_after = match.group(4)    # 62
        
        # Número de zeros indicado pelo subscrito
        num_zeros = subscript_map.get(subscript, 0)
        
        # Construir o número: before_decimal . zeros_before + (num_zeros zeros) + digits_after
        # Exemplo: 0.0₃62 -> 0.0 + 000 + 62 = 0.000062
        decimal_part = zeros_before + ('0' * num_zeros) + digits_after
        result = f"{before_decimal}.{decimal_part}"
        
        try:
            return float(result)
        except:
            pass
    
    # Fallback: tenta converter subscritos como números normais
    for sub, num in subscript_map.items():
        price_str = price_str.replace(sub, str(num))
    
    try:
        return float(price_str)
    except:
        return 0.0

