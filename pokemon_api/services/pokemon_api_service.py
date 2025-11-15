from typing import Dict, List, Optional, Any

import requests

class PokemonAPIService:
    
    def __init__(self): 
        self.session = requests.Session()
        self.base_url = 'https://pokeapi.co/api/v2/'
        
    def get_pokemon_details(self, pokemon_name: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.session.get(f"{self.base_url}/pokemon/{pokemon_name.lower()}")
            response.raise_for_status()
            data = response.json()

            return data
        except requests.RequestException:
            return None
        
    def format_pokemon_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        types = [type_info['type']['name'] for type_info in data.get('types', [])]

        abilities = [ability_info['ability']['name'] for ability_info in data.get('abilities', [])]

        stats = {stat_info['stat']['name']: stat_info['base_stat'] for stat_info in data.get('stats', [])}

        sprite_url = (
            data.get('sprites', {})
            .get('other', {})
            .get('official-artwork', {})
            .get('front_default', data.get('sprites', {}).get('front_default'))
        )

        return {
            "name": data.get("name"),
            "pokemon_id": data.get("id"),
            "types": types,
            "abilities": abilities,
            "base_stats": {
                "hp": stats.get("hp"),
                "attack": stats.get("attack"),
                "defense": stats.get("defense"),
                "special-attack": stats.get("special-attack"),
                "special-defense": stats.get("special-defense"),
                "speed": stats.get("speed"),
            },
            "height": data.get("height"),
            "weight": data.get("weight"),
            "sprite_url": sprite_url,
        }
        
    def fetch_all_pokemons(self, limit: int = 25) -> List[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/pokemon?limit={limit}")
            response.raise_for_status()
            all_pokemon = response.json()['results']
    
            detailed_pokemon = []
            for pokemon in all_pokemon:
                pokemon_data = self.get_pokemon_details(pokemon['name'])
                if pokemon_data:
                    detailed_pokemon.append(pokemon_data)
    
            return detailed_pokemon
        except requests.RequestException:
            return []
    