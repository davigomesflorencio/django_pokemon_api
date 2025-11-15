from django.contrib import admin
from .models import Pokemon

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin ):
    list_display = ('name', 'pokemon_id', 'get_types')
    search_fields = ('name', 'pokemon_id')
    
    def get_types(self, obj):
        return ", ".join(obj.types)
    get_types.short_description = 'Types'