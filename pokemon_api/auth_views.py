import logging
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from oauth2_provider.models import AccessToken
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    Endpoint para registrar um novo usuário.
    Aceita POST com username, email e password.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # Validações
        if not username or not email or not password:
            return Response(
                {"error": "Username, email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Criar novo usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return Response(
                {
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return Response(
                {"error": "An error occurred while registering the user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    """
    Endpoint para fazer login.
    Aceita POST com username e password.
    Retorna um access token OAuth2.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Autenticar usuário
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Criar ou obter token OAuth2
            # Primeiro, remover tokens expirados
            AccessToken.objects.filter(expires__lt=timezone.now()).delete()

            # Verificar se há um token válido existente
            token = AccessToken.objects.filter(user=user).first()

            if not token or token.is_expired():
                # Criar novo token
                from oauth2_provider.models import Application

                # Obter ou criar uma aplicação OAuth2
                app, _ = Application.objects.get_or_create(
                    name='Pokemon API',
                    defaults={
                        'client_type': Application.CLIENT_PUBLIC,
                        'authorization_grant_type': Application.GRANT_PASSWORD,
                    }
                )

                token = AccessToken.objects.create(
                    user=user,
                    application=app,
                    expires=timezone.now() + timedelta(hours=10),
                    scope='read write'
                )

            return Response(
                {
                    "message": "Login successful",
                    "access_token": token.token,
                    "expires_in": 36000,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return Response(
                {"error": "An error occurred during login"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    Endpoint para fazer logout.
    Requer autenticação OAuth2.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Obter o token do usuário
            token = AccessToken.objects.filter(user=request.user).first()

            if token:
                token.delete()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return Response(
                {"error": "An error occurred during logout"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """
    Endpoint para obter o perfil do usuário autenticado.
    Requer autenticação OAuth2.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            },
            status=status.HTTP_200_OK
        )
