
import logging

from django.core.cache import cache

from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# Create a logger instance
logger = logging.getLogger(__name__)
