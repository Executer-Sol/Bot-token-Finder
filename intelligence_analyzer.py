"""
Analisador de Inteligência - Analisa tokens detectados para sugerir melhores configurações
"""
from detected_tokens_tracker import get_all_detected_tokens
from typing import Dict, List, Tuple
from datetime import datetime, timezone

def analyze_detection_patterns() -> Dict:
    """Analisa padrões de detecção para sugerir configurações"""
    tokens = get_all_detected_tokens(limit=500)  # Analisa últimos 500 tokens
    
    if len(tokens) < 10:
        return {
            'enough_data': False,
            'message': 'Dados insuficientes (mínimo 10 tokens detectados)'
        }
    
    # Separa por score
    tokens_by_score = {}
    for token in tokens:
        score = token.get('score', 0)
        if score not in tokens_by_score:
            tokens_by_score[score] = []
        tokens_by_score[score].append(token)
    
    # Análise por score
    score_analysis = {}
    for score, score_tokens in tokens_by_score.items():
        if len(score_tokens) < 3:  # Precisa de pelo menos 3 tokens por score
            continue
        
        analysis = analyze_score_performance(score_tokens)
        if analysis:
            score_analysis[score] = analysis
    
    # Análise geral
    general_analysis = analyze_general_patterns(tokens)
    
    # Sugestões de configuração
    suggestions = generate_suggestions(tokens, score_analysis, general_analysis)
    
    return {
        'enough_data': True,
        'total_tokens_analyzed': len(tokens),
        'score_analysis': score_analysis,
        'general_analysis': general_analysis,
        'suggestions': suggestions,
        'tokens_by_score_count': {score: len(toks) for score, toks in tokens_by_score.items()}
    }

def analyze_score_performance(tokens: List[Dict]) -> Dict:
    """Analisa performance de um score específico"""
    times_to_peak = []
    times_to_drop = []
    peak_multiples = []
    current_multiples = []
    tokens_that_rose = 0
    tokens_that_dropped = 0
    
    for token in tokens:
        price_history = token.get('price_history', [])
        if len(price_history) < 2:
            continue
        
        initial_price = token.get('initial_price', 0)
        if initial_price <= 0:
            continue
        
        # Encontra quando atingiu o pico
        max_multiple = token.get('max_multiple', 1.0)
        max_price = token.get('max_price', initial_price)
        
        # Procura quando atingiu o pico no histórico
        peak_reached_at = None
        for i, entry in enumerate(price_history):
            entry_price = entry.get('price', initial_price)
            entry_multiple = entry_price / initial_price if initial_price > 0 else 1.0
            if entry_multiple >= max_multiple * 0.95:  # 95% do máximo (tolerância)
                peak_reached_at = entry.get('minutes_since_detection', 0)
                break
        
        if peak_reached_at is not None and peak_reached_at > 0:
            times_to_peak.append(peak_reached_at)
            peak_multiples.append(max_multiple)
        
        # Verifica se subiu ou caiu
        current_multiple = token.get('current_multiple', 1.0)
        current_multiples.append(current_multiple)
        
        if current_multiple > 1.1:  # Subiu mais de 10%
            tokens_that_rose += 1
        elif current_multiple < 0.9:  # Caiu mais de 10%
            tokens_that_dropped += 1
        
        # Encontra quando caiu significativamente (se caiu)
        if current_multiple < 0.9:
            for entry in price_history:
                entry_price = entry.get('price', initial_price)
                entry_multiple = entry_price / initial_price if initial_price > 0 else 1.0
                if entry_multiple < 0.9:  # Caiu mais de 10%
                    drop_time = entry.get('minutes_since_detection', 0)
                    times_to_drop.append(drop_time)
                    break
    
    if len(times_to_peak) == 0:
        return None
    
    avg_time_to_peak = sum(times_to_peak) / len(times_to_peak) if times_to_peak else 0
    avg_peak_multiple = sum(peak_multiples) / len(peak_multiples) if peak_multiples else 1.0
    avg_time_to_drop = sum(times_to_drop) / len(times_to_drop) if times_to_drop else 0
    avg_current_multiple = sum(current_multiples) / len(current_multiples) if current_multiples else 1.0
    
    success_rate = (tokens_that_rose / len(tokens)) * 100 if tokens else 0
    drop_rate = (tokens_that_dropped / len(tokens)) * 100 if tokens else 0
    
    return {
        'token_count': len(tokens),
        'avg_time_to_peak_minutes': round(avg_time_to_peak, 2),
        'avg_peak_multiple': round(avg_peak_multiple, 2),
        'avg_time_to_drop_minutes': round(avg_time_to_drop, 2) if times_to_drop else None,
        'avg_current_multiple': round(avg_current_multiple, 2),
        'success_rate_percent': round(success_rate, 1),
        'drop_rate_percent': round(drop_rate, 1),
        'tokens_that_rose': tokens_that_rose,
        'tokens_that_dropped': tokens_that_dropped,
        'median_time_to_peak': round(sorted(times_to_peak)[len(times_to_peak)//2], 2) if times_to_peak else 0
    }

def analyze_general_patterns(tokens: List[Dict]) -> Dict:
    """Analisa padrões gerais de todos os tokens"""
    all_times_to_peak = []
    all_peak_multiples = []
    all_current_multiples = []
    
    for token in tokens:
        initial_price = token.get('initial_price', 0)
        if initial_price <= 0:
            continue
        
        max_multiple = token.get('max_multiple', 1.0)
        current_multiple = token.get('current_multiple', 1.0)
        
        all_peak_multiples.append(max_multiple)
        all_current_multiples.append(current_multiple)
        
        # Tenta encontrar tempo até pico
        price_history = token.get('price_history', [])
        for entry in price_history:
            entry_price = entry.get('price', initial_price)
            entry_multiple = entry_price / initial_price if initial_price > 0 else 1.0
            if entry_multiple >= max_multiple * 0.95:
                all_times_to_peak.append(entry.get('minutes_since_detection', 0))
                break
    
    if len(all_times_to_peak) == 0:
        return {}
    
    return {
        'avg_time_to_peak_all_scores': round(sum(all_times_to_peak) / len(all_times_to_peak), 2),
        'median_time_to_peak': round(sorted(all_times_to_peak)[len(all_times_to_peak)//2], 2),
        'avg_peak_multiple': round(sum(all_peak_multiples) / len(all_peak_multiples), 2),
        'avg_current_multiple': round(sum(all_current_multiples) / len(all_current_multiples), 2),
        'tokens_analyzed': len(tokens)
    }

def generate_suggestions(tokens: List[Dict], score_analysis: Dict, general_analysis: Dict) -> Dict:
    """Gera sugestões de configuração baseado na análise"""
    suggestions = {
        'stop_loss_time': None,
        'stop_loss_percent': None,
        'take_profit_multiple': None,
        'best_scores': [],
        'worst_scores': []
    }
    
    # Analisa tempo médio até pico para sugerir stop loss
    if general_analysis and 'avg_time_to_peak_all_scores' in general_analysis:
        avg_time = general_analysis['avg_time_to_peak_all_scores']
        # Sugere stop loss time = 1.5x o tempo médio até pico (com mínimo de 3 min, máximo de 10 min)
        suggested_time = max(3, min(10, int(avg_time * 1.5)))
        suggestions['stop_loss_time'] = suggested_time
    
    # Analisa scores para identificar melhores/piores
    if score_analysis:
        score_performances = []
        for score, analysis in score_analysis.items():
            score_performances.append({
                'score': score,
                'success_rate': analysis.get('success_rate_percent', 0),
                'avg_peak_multiple': analysis.get('avg_peak_multiple', 1.0),
                'avg_time_to_peak': analysis.get('avg_time_to_peak_minutes', 0)
            })
        
        # Ordena por sucesso
        score_performances.sort(key=lambda x: x['success_rate'], reverse=True)
        
        if score_performances:
            suggestions['best_scores'] = [s['score'] for s in score_performances[:3]]
            suggestions['worst_scores'] = [s['score'] for s in score_performances[-3:]]
    
    # Sugere take profit baseado no múltiplo médio de pico
    if general_analysis and 'avg_peak_multiple' in general_analysis:
        avg_peak = general_analysis['avg_peak_multiple']
        # Sugere TP em 70% do múltiplo médio de pico (para garantir venda antes de cair)
        suggested_tp = round(avg_peak * 0.7, 1)
        suggestions['take_profit_multiple'] = max(1.5, min(5.0, suggested_tp))  # Entre 1.5x e 5.0x
    
    return suggestions

def get_intelligence_data() -> Dict:
    """Retorna dados de inteligência para a API"""
    return analyze_detection_patterns()





