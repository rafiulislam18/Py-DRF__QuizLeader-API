from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer, DeviceSerializer
from .models import Device
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
    
    def post(self, request):
        # Handle user login with device ID optimization
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device_id = serializer.validated_data['device_id']
        device = Device.objects.filter(device_id=device_id).first()
        
        if device:
            user = device.user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
            
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)
            
        Device.objects.create(user=user, device_id=device_id)
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
