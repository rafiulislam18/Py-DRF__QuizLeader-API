from .base import *
from ..serializers import (
    CustomUserSerializer,
    LoginSerializer,
    LoginResponseSerializer
)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterLoginThrottle]

    # Handle user login and return JWT tokens
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Login user & get JWT tokens",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                'Success: Ok',
                LoginResponseSerializer
            ),
            400: 'Error: Bad request',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(
                data=request.data,
                context={'request': request}
            )
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

            return Response(
                LoginResponseSerializer(response).data,
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LoginView.post(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
