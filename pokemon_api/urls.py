from django.urls import path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Pokemon Davi Gomes Florencio",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from pokemon_api.views import PokemonAPIView, PokemonManagementView, PokemonScoreView

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/pokemon/', PokemonAPIView.as_view(), name='pokemon_api'),    
    path('pokemon/', PokemonManagementView.as_view(), name='pokemon_management'),
    path('pokemon/<uuid:id>/', PokemonManagementView.as_view(), name='pokemon_management_detail'),
    path('pokemon/score/<uuid:id>/', PokemonScoreView.as_view(), name='pokemon_score'),
]