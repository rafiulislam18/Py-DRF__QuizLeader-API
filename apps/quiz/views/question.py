from django.core.exceptions import ValidationError as DjangoValidationError

from .base import *
from ..models import Lesson, Question
from ..paginators import QuestionListPagination
from ..serializers import (
    QuestionSerializer,
    QuestionResponseSerializer,
    QuestionPaginatedResponseSerializer
)


class QuestionView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = QuestionListPagination
    
    def get_cache_key(self, lesson_id, page_number, page_size):
        return f'questions_for_lesson_{lesson_id}_page_{page_number}_size_{page_size}'

    # Get/retrieve all questions for a lesson
    @swagger_auto_schema(
        tags=["Quiz-Questions"],
        operation_description="Get/retrieve all questions within a lesson",
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
                description=(
                    f"Number of results per page (default: {QuestionListPagination.page_size}, "
                    f"max: {QuestionListPagination.max_page_size})"
                ),
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                QuestionPaginatedResponseSerializer
            ),
            400: 'Error: Bad Request',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, lesson_id):
        try:
            # Get current page from request
            page_number = request.query_params.get('page', 1)

            # Get page size from request, default to the pagination class default
            page_size = request.query_params.get(
                'page_size',
                self.pagination_class.page_size
            )
            
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
            # Log the error for debugging
            logger.error(
                f"Error in QuestionView.get(): {str(e)}",
                exc_info=True
            )

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
            201: openapi.Response(
                'Success: Created',
                QuestionResponseSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
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

            return Response(
                QuestionResponseSerializer(question).data,
                status=status.HTTP_201_CREATED
            )
        
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
            # Log the error for debugging
            logger.error(
                f"Error in QuestionView.post(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
