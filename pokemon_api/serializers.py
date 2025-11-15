from rest_framework import serializers

from .models import Pokemon


class PokemonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pokemon
        fields = [
            'id', 'created_at', 'updated_at', 'name', 'pokemon_id',
            'types', 'abilities', 'base_stats', 'height', 'weight', 'sprite_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']