from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Max, Avg, Count, F
from .models import Subject, Lesson, Question, QuizAttempt
from .serializers import SubjectSerializer, LessonSerializer, LessonResponseSerializer, QuestionSerializer, QuestionResponseSerializer, QuizStartResponseSerializer, QuestionPaginatedResponseSerializer, SubjectPaginatedResponseSerializer, LessonPaginatedResponseSerializer
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
from .paginators import SubjectListPagination, LessonListPagination, QuestionListPagination
from django.core.cache import cache
import logging


# Create a logger instance
logger = logging.getLogger(__name__)


class QuizStartView(APIView):
    permission_classes = [IsAuthenticated]

    # Start a new quiz with randomized questions for a lesson
    @swagger_auto_schema(
        tags=["Quiz-Game"],
        operation_description="Start a new quiz with up to 15 randomized questions for a lesson",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to start quiz for",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response('Success: Quiz start successful', QuizStartResponseSerializer),
            400: 'Error: Bad request',
            401: 'Error: Unauthorized',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)

            # Get a list of question IDs for the lesson
            question_ids = list(lesson.questions.values_list('id', flat=True))
            
            # Select random IDs (up to 15)
            selected_ids = random.sample(
                question_ids, 
                min(len(question_ids), 15)
            )
            
            # Fetch only the selected questions
            questions = lesson.questions.filter(id__in=selected_ids)
            
            # Create a new quiz attempt
            attempt = QuizAttempt.objects.create(
                user=request.user,
                lesson=lesson,
                score=0
            )
            
            return Response({
                'attempt_id': attempt.id,
                'questions': QuestionResponseSerializer(questions, many=True).data
            })
        
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error in QuizStartView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class QuestionView(APIView):
    pagination_class = QuestionListPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_cache_key(self, lesson_id, page_number, page_size):
        return f'questions_for_lesson_{lesson_id}_page_{page_number}_size_{page_size}'

    # Get/retrieve all questions for a lesson
    @swagger_auto_schema(
        tags=["Quiz-Questions"],
        operation_description="Get/retrieve all questions of a lesson",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to get questions for",
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
                description=f"Number of results per page (default: {QuestionListPagination.page_size}, max: {QuestionListPagination.max_page_size})",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response('Success: Get questions successful', QuestionPaginatedResponseSerializer),
            400: 'Error: Bad Request',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, lesson_id):
        try:
            # Get current page from request
            page_number = request.query_params.get('page', 1)

            # Get page size from request, default to the pagination class default
            page_size = request.query_params.get('page_size', self.pagination_class.page_size)
            
            cache_key = self.get_cache_key(lesson_id, page_number, page_size)  # Unique key for caching questions
            questions = cache.get(cache_key)  # Try getting cached data

            if not questions:  # If empty cache
                questions = Question.objects.filter(lesson__id=lesson_id)

                if not questions.exists():
                    return Response(
                        {"detail": "No questions found for the given lesson."},
                        status=status.HTTP_404_NOT_FOUND
                    )
                cache.set(cache_key, questions, timeout=60*15)  # Cache for 15 minutes

            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(questions, request)
            if page is not None:
                serializer = QuestionResponseSerializer(page, many=True)
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
            logger.error(f"Error in QuestionView.get(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Create a new question within a lesson
    @swagger_auto_schema(
        tags=["Quiz-Questions"],
        operation_description="Create a new question within a lesson",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to create question for",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text', 'options', 'correct_answer'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The question text'
                ),
                'options': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Three options numbered 1-3',
                    properties={
                        '1': openapi.Schema(type=openapi.TYPE_STRING),
                        '2': openapi.Schema(type=openapi.TYPE_STRING),
                        '3': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    required=['1', '2', '3']
                ),
                'correct_answer': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='The correct option number (1, 2, or 3)'
                )
            },
            example={
                "text": "What is the capital of France?",
                "options": {
                    "1": "Paris",
                    "2": "London",
                    "3": "Berlin"
                },
                "correct_answer": 1
            }
        ),
        responses={
            201: openapi.Response('Success: Question creation successful', QuestionResponseSerializer),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)

            serializer = QuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            question = serializer.save(lesson=lesson)

            cache.clear()  # Invalidate cache as database updated
            return Response(QuestionResponseSerializer(question).data, status=status.HTTP_201_CREATED)
        
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except DjangoValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error in QuestionView.post(): {str(e)}", exc_info=True)  # Log the error for debugging
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
