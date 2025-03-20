from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Max, Avg, Count, F
from .models import Subject, Lesson, Question, QuizAttempt
from .serializers import SubjectSerializer, LessonSerializer, LessonResponseSerializer, LessonPaginatedResponseSerializer
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
from .paginators import SubjectListPagination, LessonListPagination
from django.core.cache import cache
import logging


# Create a logger instance
logger = logging.getLogger(__name__)


class SubjectView(APIView):
    pagination_class = SubjectListPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_cache_key(self, page_number, page_size):
        return f'subject_page_{page_number}_size_{page_size}'

    # Get/retrieve all subjects
    @swagger_auto_schema(
        tags=["Quiz-Subjects"],
        operation_description="Get/retrieve all subjects",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number (default: 1)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description=f"Number of results per page (default: {SubjectListPagination.page_size}, max: {SubjectListPagination.max_page_size})",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response('Success: Get subjects successful', SubjectPaginatedResponseSerializer),
            400: 'Error: Bad Request',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request):
        try:
            # Get current page from request
            page_number = request.query_params.get('page', 1)

            # Get page size from request, default to the pagination class default
            page_size = request.query_params.get('page_size', self.pagination_class.page_size)

            cache_key = self.get_cache_key(page_number, page_size)  # Unique key for caching subjects
            subjects = cache.get(cache_key)  # Try getting cached data

            if not subjects:  # If empty cache
                subjects = Subject.objects.all().order_by('name')

                if not subjects.exists():
                    return Response(
                        {"detail": "No subjects found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
                cache.set(cache_key, subjects, timeout=60*15)  # Cache for 15 minutes
            
            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(subjects, request)
            if page is not None:
                serializer = SubjectSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            # If pagination is not applied, throw an error
            return Response(
                {"error": "Pagination is required for this endpoint."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except NotFound as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            logger.error(f"Error in SubjectView.get(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Create a new subject
    @swagger_auto_schema(
        tags=["Quiz-Subjects"],
        operation_description="Create a new subject",
        request_body=SubjectSerializer,
        responses={
            201: openapi.Response('Success: Subject creation successful', SubjectSerializer),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = SubjectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            cache.clear()  # Invalidate cache as database updated
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error in SubjectView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LessonView(APIView):
    pagination_class = LessonListPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_cache_key(self, subject_id, page_number, page_size):
        return f'lessons_for_subject_{subject_id}_page_{page_number}_size_{page_size}'

    # Get/retrieve all lessons for a subject
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Get/retrieve all lessons of a subject",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to get lessons for",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number (default: 1)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description=f"Number of results per page (default: {LessonListPagination.page_size}, max: {LessonListPagination.max_page_size})",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response('Success: Get lessons successful', LessonPaginatedResponseSerializer),
            400: 'Error: Bad Request',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, subject_id):
        try:
            # Get current page from request
            page_number = request.query_params.get('page', 1)

            # Get page size from request, default to the pagination class default
            page_size = request.query_params.get('page_size', self.pagination_class.page_size)

            cache_key = self.get_cache_key(subject_id, page_number, page_size)  # Unique key for caching lessons
            lessons = cache.get(cache_key)  # Try getting cached data

            if not lessons:  # If empty cache
                lessons = Lesson.objects.filter(subject__id=subject_id)

                if not lessons.exists():
                    return Response(
                        {"detail": "No lessons found for the given subject."},
                        status=status.HTTP_404_NOT_FOUND
                    )
                cache.set(cache_key, lessons, timeout=60*15)  # Cache for 15 minutes

            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(lessons, request)
            if page is not None:
                serializer = LessonResponseSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            # If pagination is not applied, throw an error
            return Response(
                {"error": "Pagination is required for this endpoint."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except NotFound as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            logger.error(f"Error in LessonView.get(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Create a new lesson within a subject
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Create a new lesson within a subject",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to create lesson for",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=LessonSerializer,
        responses={
            201: openapi.Response('Success: Lesson creation successful', LessonResponseSerializer),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
        
            serializer = LessonSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(subject=subject)

            cache.clear()  # Invalidate cache as database updated
            return Response(LessonResponseSerializer(lesson).data, status=status.HTTP_201_CREATED)
        
        except Subject.DoesNotExist:
            return Response(
                {"detail": "Subject not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error in LessonView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
