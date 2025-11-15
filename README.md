# Projeto Pokémon API

## Visão geral

Este projeto fornece uma API em Django para consultar dados de Pokémons usando a PokeAPI (https://pokeapi.co/) e armazenar entradas locais em um banco SQLite. Também inclui cálculo de "score" para cada Pokémon com base nos seus status.

## Objetivos do projeto

- Demonstrar integração com APIs externas (PokeAPI).
- Fornecer endpoints REST para consultar, salvar e gerenciar Pokémons.
- Implementar autenticação OAuth2 para proteger operações sensíveis.
- Expor cálculo de score baseado em estatísticas dos Pokémons.

## Principais tecnologias

- Python 3.10+ / Django 4.2
- Django REST Framework (DRF)
- django-oauth-toolkit (OAuth2)
- requests (para comunicação com a PokeAPI)
- SQLite (banco de dados por padrão)

## Instalação rápida

1. Criar e ativar um ambiente virtual (recomendado).

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Rodar migrações e criar superuser:

```pwsh
python manage.py migrate
python manage.py createsuperuser
```

3. Iniciar o servidor de desenvolvimento:

```pwsh
python manage.py runserver
```

## Autenticação

Este projeto inclui `django-oauth-toolkit`. As URLs do provedor OAuth2 são expostas em `/o/` (ex.: `/o/token/`, `/o/authorize/`, etc.).

Observação: existe uma implementação local em `pokemon_api/auth_views.py` com endpoints de `Register`, `Login`, `Logout` e `UserProfile`, mas esses endpoints precisam ser registrados nas rotas para ficarem ativos (podemos adicioná-los em `pokemon_api/urls.py` se desejar).

## Fluxo de autenticação sugerido

- Criar uma aplicação OAuth2 via admin (/admin/) ou usar o endpoint de criação de aplicações.
- Trocar credenciais pelo token (via grant apropriado) ou usar o endpoint personalizado `/auth/login/` se for exposto.
- Enviar o token nas requisições com o header: `Authorization: Bearer <access_token>`.

## Endpoints principais

As rotas atualmente expostas pelo projeto (arquivo `pokemon_api/urls.py`):

- `GET /api/pokemon/?name=<nome>` — Busca detalhes de um Pokémon pela PokeAPI e retorna dados formatados.
- `POST /api/pokemon/?limit=<n>` — (implementado) Busca os primeiros `<n>` Pokémons da PokeAPI e salva/atualiza no banco local (padrão: 25). Requer autenticação para execução segura.
- `GET /pokemon/` — Lista todos os Pokémons salvos localmente.
- `POST /pokemon/` — Cria um novo Pokémon local (envia JSON com campos do modelo).
- `GET /pokemon/<uuid:id>/` — Obtém um Pokémon específico pelo `id`.
- `PATCH /pokemon/<uuid:id>/` — Atualiza parcialmente um Pokémon existente.
- `DELETE /pokemon/<uuid:id>/` — Remove um Pokémon do banco.
- `GET /pokemon/score/<uuid:id>/` — Calcula e retorna o "score" do Pokémon com base nos seus status.

Também estão disponíveis as URLs do provedor OAuth2:

- `/o/` — Namespace do `django-oauth-toolkit` (ex.: `/o/token/`).

## Exemplos rápidos (curl)

- Registrar usuário (se exposto):

```bash
curl -X POST http://127.0.0.1:8000/auth/register/ -H "Content-Type: application/json" -d '{"username":"demo","email":"demo@example.com","password":"senha1234"}'
```

- Login (usando endpoint customizado se disponível):

```bash
curl -X POST http://127.0.0.1:8000/auth/login/ -H "Content-Type: application/json" -d '{"username":"demo","password":"senha1234"}'
```

- Consultar Pokémon (com token):

```bash
curl -H "Authorization: Bearer <TOKEN>" "http://127.0.0.1:8000/api/pokemon/?name=pikachu"
```

## Notas finais

- Arquivo de configurações: `backend_pokemon/settings.py` contém as configurações do DRF e do `oauth2_provider`.
- Modelo `Pokemon` está em `pokemon_api/models.py` e usa `JSONField` para `types`, `abilities` e `base_stats`.
- Se quiser, posso:
  - Registrar os endpoints de autenticação (`auth_views`) nas rotas automaticamente;
  - Forçar autenticação nas outras views (`PokemonManagementView`, `PokemonScoreView`) e ajustar permissões;
  - Adicionar exemplos de payload para criação de Pokémon.

## Licença

Projeto para fins educacionais/demonstração.
