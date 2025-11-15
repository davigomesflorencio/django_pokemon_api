from django.urls import path

from pokemon_api.views import PokemonAPIView, PokemonManagementView, PokemonScoreView

urlpatterns = [
    path('api/pokemon/', PokemonAPIView.as_view(), name='pokemon_api'),    
    path('pokemon/', PokemonManagementView.as_view(), name='pokemon_management'),
    path('pokemon/<uuid:id>/', PokemonManagementView.as_view(), name='pokemon_management_detail'),
    path('pokemon/score/<uuid:id>/', PokemonScoreView.as_view(), name='pokemon_score'),
]