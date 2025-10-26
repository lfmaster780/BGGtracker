from typing import Dict, List, Any
from collections import Counter
import numpy as np

class PreferenceAnalyzer:
    def __init__(self, collection: List[Dict]):
        self.collection = collection
    
    def analyze_preferences(self) -> Dict[str, Any]:
        """Analisa preferências baseado na coleção"""
        if not self.collection:
            return self._get_empty_preferences()
        
        return {
            'total_games': len(self.collection),
            'avg_rating': self._calculate_avg_rating(),
            'avg_complexity': self._calculate_avg_complexity(),
            'rating_tendency': self._analyze_rating_tendency(),
            'preferred_complexity': self._get_preferred_complexity()
        }
    
    def _get_empty_preferences(self) -> Dict:
        return {
            'total_games': 0,
            'avg_rating': 0,
            'avg_complexity': 0,
            'rating_tendency': 'Neutro',
            'preferred_complexity': 'Variado'
        }
    
    def _calculate_avg_rating(self) -> float:
        ratings = [game.get('my_rating', 0) for game in self.collection if game.get('my_rating', 0) > 0]
        return round(np.mean(ratings), 2) if ratings else 0
    
    def _calculate_avg_complexity(self) -> float:
        complexities = [game.get('complexity', 0) for game in self.collection if game.get('complexity', 0) > 0]
        return round(np.mean(complexities), 2) if complexities else 0
    
    def _analyze_rating_tendency(self) -> str:
        user_ratings = [g.get('my_rating', 0) for g in self.collection if g.get('my_rating', 0) > 0]
        bgg_ratings = [g.get('bgg_rating', 0) for g in self.collection if g.get('bgg_rating', 0) > 0]
        
        if not user_ratings or not bgg_ratings:
            return "Neutro"
        
        user_avg = np.mean(user_ratings)
        bgg_avg = np.mean(bgg_ratings)
        diff = user_avg - bgg_avg
        
        if diff > 1: return "Generoso"
        elif diff > 0.5: return "Levemente Generoso"
        elif diff < -1: return "Exigente"
        elif diff < -0.5: return "Levemente Exigente"
        else: return "Neutro"
    
    def _get_preferred_complexity(self) -> str:
        complexities = [g.get('complexity', 0) for g in self.collection if g.get('complexity', 0) > 0]
        if not complexities:
            return "Variado"
        
        avg = np.mean(complexities)
        if avg < 2: return "Leve"
        elif avg < 3: return "Moderada"
        else: return "Complexa"