from rest_framework_simplejwt.views import TokenRefreshView

from .base import *
from ..serializers import (
    TokenRefreshResponseSerializer
)


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

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
                'Success: Token refresh successful',
                TokenRefreshResponseSerializer
            ),
            401: 'Error: Unauthorized',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
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
