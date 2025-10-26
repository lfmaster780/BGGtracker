import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import time
import re


class BGGAPI:
    def __init__(self):
        self.base_url = "https://boardgamegeek.com/xmlapi2"
        self.delay = 1

    def get_user_collection(self, username: str) -> List[Dict]:
        """Busca coleção do usuário no BGG"""
        try:
            url = f"{self.base_url}/collection?username={username}&stats=1"
            response = requests.get(url)

            if response.status_code == 202:
                time.sleep(2)
                response = requests.get(url)

            response.raise_for_status()
            root = ET.fromstring(response.content)

            games = []
            for item in root.findall("item"):
                if (
                    item.get("subtype") == "boardgame"
                    and item.find("status") is not None
                    and item.find("status").get("own") == "1"
                ):
                    game_data = {
                        "id": item.get("objectid"),
                        "name": item.find("name").text
                        if item.find("name") is not None
                        else "N/A",
                        "year": item.find("yearpublished").text
                        if item.find("yearpublished") is not None
                        else "N/A",
                        "image": item.find("image").text
                        if item.find("image") is not None
                        else "",
                        "thumbnail": item.find("thumbnail").text
                        if item.find("thumbnail") is not None
                        else "",
                        "my_rating": self._get_my_rating(item),
                        "bgg_rating": self._get_bgg_rating(item),
                        "complexity": self._get_complexity(item),
                        "num_plays": item.find("numplays").text
                        if item.find("numplays") is not None
                        else "0",
                    }
                    games.append(game_data)

            return games

        except Exception as e:
            print(f"Erro ao buscar coleção: {e}")
            return []

    def _get_my_rating(self, item) -> float:
        rating = item.find("stats/rating")
        if rating is not None and rating.get("value") != "N/A":
            try:
                return float(rating.get("value"))
            except:
                return 0.0
        return 0.0

    def _get_bgg_rating(self, item) -> float:
        stats = item.find("stats")
        if stats is not None:
            rating = stats.find("rating/average")
            if rating is not None:
                try:
                    return float(rating.get("value"))
                except:
                    return 0.0
        return 0.0

    def _get_complexity(self, item) -> float:
        """Extrai a complexidade (weight) - VERSÃO CORRIGIDA"""
        try:
            # O caminho correto é: stats -> rating -> averageweight
            stats = item.find("stats")
            if stats is not None:
                rating = stats.find("rating")
                if rating is not None:
                    weight = rating.find("averageweight")
                    if weight is not None:
                        return float(weight.get("value"))
            return 0.0
        except Exception as e:
            print(f"Erro ao extrair complexidade: {e}")
            return 0.0
