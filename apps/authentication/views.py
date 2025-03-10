from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer, DeviceSerializer
from .models import Device
from rest_framework.permissions import AllowAny


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
