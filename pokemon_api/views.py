import logging 

from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, GenericAPIView

from pokemon_api.serializers import PokemonSerializer
from pokemon_api.models import Pokemon
from pokemon_api.services.pokemon_api_service import PokemonAPIService
from pokemon_api.services.score_service import ScoreService

logger = logging.getLogger(__name__)

class PokemonAPIView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
     
    def retrieve(self, request, *args, **kwargs):
        pokemon_name = request.query_params.get('name')
        service = PokemonAPIService()

        try:
            pokemon_details = service.get_pokemon_details(pokemon_name=pokemon_name)

            if not pokemon_details:
                return Response({"error": "Pokemon not found"}, status=status.HTTP_404_NOT_FOUND)

            formatted_data = service.format_pokemon_data(pokemon_details)
            return Response(formatted_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching Pokemon data: {e}")
            return Response({"error": "An error occurred while fetching Pokemon data"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        """
        Salva uma lista de pokémons obtidos do método fetch_all_pokemons.
        Aceita um parâmetro opcional 'limit' para especificar quantos pokémons buscar.
        """
        limit = request.query_params.get('limit', 25)
        
        try:
            limit = int(limit)
        except ValueError:
            return Response(
                {"error": "The 'limit' parameter must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = PokemonAPIService()

        try:
            # Busca todos os pokémons da API
            all_pokemons = service.fetch_all_pokemons(limit=limit)

            if not all_pokemons:
                return Response(
                    {"error": "Failed to fetch pokemons from API"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Salva os pokémons no banco de dados
            created_count = 0
            skipped_count = 0
            errors = []

            for pokemon_data in all_pokemons:
                try:
                    # Formata os dados antes de salvar
                    formatted_data = service.format_pokemon_data(pokemon_data)
                    
                    # Cria ou atualiza o pokémon no banco
                    pokemon, created = Pokemon.objects.update_or_create(
                        name=formatted_data['name'],
                        defaults={
                            'pokemon_id': formatted_data['pokemon_id'],
                            'types': formatted_data['types'],
                            'abilities': formatted_data['abilities'],
                            'base_stats': formatted_data['base_stats'],
                            'height': formatted_data['height'],
                            'weight': formatted_data['weight'],
                            'sprite_url': formatted_data['sprite_url'],
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    logger.error(f"Error saving Pokemon {pokemon_data.get('name')}: {e}")
                    errors.append({
                        "name": pokemon_data.get('name'),
                        "error": str(e)
                    })

            response_data = {
                "message": "Pokémons saved successfully",
                "created": created_count,
                "updated": skipped_count,
                "total_processed": created_count + skipped_count,
            }

            if errors:
                response_data["errors"] = errors

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error fetching and saving Pokemon list: {e}")
            return Response(
                {"error": "An error occurred while fetching and saving Pokemon data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class PokemonManagementView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PokemonSerializer
    queryset = Pokemon.objects.all()
    lookup_field = "id"

    def get(self, request, id=None):
        name = request.query_params.get('name')

        if id:
            pokemon = get_object_or_404(self.get_queryset(), id=id)
            serializer = self.get_serializer(pokemon)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif name:
            pokemon = get_object_or_404(self.get_queryset(), name=name)
            serializer = self.get_serializer(pokemon)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            pokemons = self.get_queryset()
            serializer = self.get_serializer(pokemons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id=None):
        pokemon = get_object_or_404(self.get_queryset(), id=id)
        serializer = self.get_serializer(pokemon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        pokemon = get_object_or_404(self.get_queryset(), id=id)
        pokemon.delete()
        return Response({"message": f"Pokemon with id '{id}' deleted successfully."}, status=status.HTTP_200_OK)


class PokemonScoreView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    score_service = ScoreService()

    def get(self, request, id=None):
        try:
            pokemon = get_object_or_404(Pokemon, id=id)

            base_stats_list = list(pokemon.base_stats.values())
            pokemon_data = {
                'types': pokemon.types,
                'base_stats': base_stats_list,
                'abilities': pokemon.abilities,
                'height': pokemon.height,
                'weight': pokemon.weight,
            }

            score = self.score_service.calculate_score(pokemon_data)

            return Response({
                'name': pokemon.name,
                'score': score
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error calculating score: {e}")
            return Response({"error": "An error occurred while calculating the score."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)