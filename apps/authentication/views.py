from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from .serializers import CustomUserSerializer, RegisterSerializer, RegisterResponseSerializer, LoginSerializer, LoginResponseSerializer, LogoutSerializer, LogoutResponseSerializer, TokenRefreshResponseSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging


# Create a logger instance
logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    # Register a new user
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Register a new user & get JWT tokens",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response('Success: Registration successful', RegisterResponseSerializer),
            400: 'Error: Bad request',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = {
                'refresh': str(refresh),
                'access': access_token,
                'id': user.id,
                'username': user.username,
            }

            return Response(RegisterResponseSerializer(response).data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error in RegisterView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    # Handle user login and return JWT tokens
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Login user & get JWT tokens",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response('Success: Login successful', LoginResponseSerializer),
            400: 'Error: Bad request',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = {
                'refresh': str(refresh),
                'access': access_token,
                'user': CustomUserSerializer(user).data
            }

            return Response(LoginResponseSerializer(response).data)
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error in LoginView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    # Handle user logout
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Logout user by refresh token",
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response('Success: Logout successful', LogoutResponseSerializer),
            400: 'Error: Bad request',
            401: 'Error: Unauthorized',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

            response = {"detail": "Logout successful."}

            return Response(
                LogoutResponseSerializer(response).data,
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except TokenError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            logger.error(f"Error in LogoutView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
