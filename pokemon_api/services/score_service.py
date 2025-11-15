from typing import Dict, List, Any

class ScoreService:
    def __init__(self):
        self.weights = {
            'types': 0.4,
            'base_stats': 0.3,
            'abilities': 0.2,
            'physical': 0.1
        }

    def calculate_score(self, pokemon_data: Dict[str, Any]) -> float:
        score = 0

        type_score = self._calculate_type_score(pokemon_data['types'])
        score += type_score * self.weights['types']

        stats_score = self._calculate_stats_score(pokemon_data['base_stats'])
        score += stats_score * self.weights['base_stats']

        abilities_score = self._calculate_abilities_score(pokemon_data['abilities'])
        score += abilities_score * self.weights['abilities']

        physical_score = self._calculate_physical_score(pokemon_data['height'], pokemon_data['weight'])
        score += physical_score * self.weights['physical']

        return round(score, 2)

    def _calculate_type_score(self, types: List[str]) -> float:
        base_score = len(types) * 50

        return min(base_score, 100)

    def _calculate_stats_score(self, base_stats) -> float:
        if not isinstance(base_stats, list) or not all(isinstance(stat, int) for stat in base_stats):
            raise ValueError("base_stats must be a list of integers")

        total_stats = sum(base_stats)
        return total_stats

    def _calculate_abilities_score(self, abilities: List[str]) -> float:
        base_score = len(abilities) * 33.33

        return min(base_score, 100)

    def _calculate_physical_score(self, height: float, weight: float) -> float:
        height_score = min(height * 5, 50)
        weight_score = min(weight / 20, 50)

        return height_score + weight_score