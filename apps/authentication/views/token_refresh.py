from rest_framework_simplejwt.views import TokenRefreshView

from .base import *
from ..serializers import (
    TokenRefreshResponseSerializer
)


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    throttle_classes = [HighLimitAnonRateThrottle]

    # Handle token refresh
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description=(
            "Takes a refresh type JSON web token and returns an access type "
            "JSON web token & a new refresh token blacklisting the previous "
            "one if the submitted refresh token is valid."
        ),
        responses={
            200: openapi.Response(
                'Success: Ok',
                TokenRefreshResponseSerializer
            ),
            400: 'Error: Bad request',
            401: 'Error: Unauthorized',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # Check if refresh token is not provided
            if not request.data.get('refresh'):
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return super().post(request, *args, **kwargs)
        
        except InvalidToken as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except TokenError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in MyTokenRefreshView.post(): {str(e)}",
                exc_info=True
            )
            
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
