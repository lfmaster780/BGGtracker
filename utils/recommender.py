from typing import Dict, List
import requests
import xml.etree.ElementTree as ET
import time

class GameRecommender:
    def __init__(self):
        self.base_url = "https://boardgamegeek.com/xmlapi2"
    
    def get_recommendations(self, user_complexity: float) -> List[Dict]:
        """Busca jogos populares que combinam com a complexidade preferida"""
        try:
            url = f"{self.base_url}/hot?type=boardgame"
            response = requests.get(url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            recommendations = []
            
            for item in root.findall('item')[:10]:  # Top 10 populares
                game_id = item.get('id')
                game_data = {
                    'id': game_id,
                    'name': item.find('name').get('value'),
                    'year': item.find('yearpublished').get('value') if item.find('yearpublished') is not None else 'N/A'
                }
                
                # Buscar complexidade
                details = self._get_game_details(game_id)
                if details:
                    game_data.update(details)
                    # Calcular match score baseado na complexidade
                    game_complexity = details.get('complexity', 0)
                    complexity_diff = abs(game_complexity - user_complexity)
                    game_data['match_score'] = max(0, 100 - (complexity_diff * 30))
                    game_data['reason'] = self._generate_reason(game_complexity, user_complexity)
                
                recommendations.append(game_data)
                time.sleep(0.5)  # Rate limiting
            
            return sorted(recommendations, key=lambda x: x.get('match_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Erro ao buscar recomendações: {e}")
            return []
    
    def _get_game_details(self, game_id: str) -> Dict:
        try:
            url = f"{self.base_url}/thing?id={game_id}&stats=1"
            response = requests.get(url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            item = root.find('item')
            
            if item is not None:
                complexity = 0.0
                stats = item.find('stats')
                if stats is not None:
                    weight = stats.find('rating/averageweight')
                    if weight is not None:
                        complexity = float(weight.get('value'))
                
                return {
                    'complexity': complexity,
                    'min_players': item.find('minplayers').get('value'),
                    'max_players': item.find('maxplayers').get('value'),
                    'playtime': item.find('playingtime').get('value')
                }
            return {}
            
        except Exception as e:
            print(f"Erro nos detalhes do jogo {game_id}: {e}")
            return {}
    
    def _generate_reason(self, game_complexity: float, user_complexity: float) -> str:
        diff = game_complexity - user_complexity
        if abs(diff) <= 0.5:
            return "Complexidade similar à sua preferência"
        elif diff > 0.5:
            return "Um pouco mais complexo que seu usual"
        else:
            return "Um pouco mais leve que seu usual"