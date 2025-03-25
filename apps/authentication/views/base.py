import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..throttles import RegisterLoginThrottle, HighLimitAnonRateThrottle


# Create a logger instance
logger = logging.getLogger(__name__)
