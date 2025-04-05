from django.db.utils import IntegrityError

from .base import *
from ..models import Subject, Lesson
from ..paginators import LessonListPagination
from ..serializers import (
    LessonSerializer,
    LessonResponseSerializer,
    LessonPaginatedResponseSerializer
)


class LessonListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LessonListPagination
    
    def get_cache_key(self, subject_id, page_number, page_size):
        return f'lessons:subject:{subject_id}:page:{page_number}:size:{page_size}'

    # Get/retrieve all lessons for a subject
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_id="quiz_lessons_list",
        operation_description="Get/retrieve all lessons within a subject",
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
                description=(
                    f"Number of results per page (default: {LessonListPagination.page_size}, "
                    f"max: {LessonListPagination.max_page_size})"
                ),
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                LessonPaginatedResponseSerializer
            ),
            400: 'Error: Bad Request',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, subject_id):
        try:
            # Check if the subject exists
            subject = Subject.objects.get(id=subject_id)  

            # Get current page from request
            page_number = request.query_params.get('page', 1)

            # Get page size from request, default to the pagination class default
            page_size = request.query_params.get(
                'page_size',
                self.pagination_class.page_size
            )

            cache_key = self.get_cache_key(subject_id, page_number, page_size)  # Unique key for caching lessons
            lessons = cache.get(cache_key)  # Try getting cached data

            if not lessons:  # If empty cache
                lessons = Lesson.objects.filter(subject=subject)

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
        
        except Subject.DoesNotExist:
            return Response(
                {"detail": "Subject not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except NotFound as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LessonListCreateView.get(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Create a new lesson within a subject
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_id="quiz_lessons_create",
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
            201: openapi.Response(
                'Success: Created',
                LessonResponseSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
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

            return Response(
                LessonResponseSerializer(lesson).data,
                status=status.HTTP_201_CREATED
            )
        
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
        
        except IntegrityError as e:
            return Response(
                {"detail": "Duplicate lesson title found within the same subject."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LessonListCreateView.post(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LessonDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    # Get/retrieve a lesson by ID
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Get/retrieve a lesson by ID",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                LessonResponseSerializer
            ),
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            return Response(
                LessonResponseSerializer(lesson).data,
                status=status.HTTP_200_OK
            )
        
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LessonDetailView.get(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Update a lesson by ID using PUT method
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Update a lesson by ID using PUT method",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=LessonSerializer,
        responses={
            200: openapi.Response(
                'Success: Ok',
                LessonResponseSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def put(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)

            serializer = LessonSerializer(lesson, data=request.data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save()

            cache.clear()  # Invalidate cache as database updated

            return Response(
                LessonResponseSerializer(lesson).data,
                status=status.HTTP_200_OK
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
        
        except IntegrityError as e:
            return Response(
                {"detail": "Duplicate lesson title found within the same subject."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LessonDetailView.put(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # Update a lesson by ID using PATCH method
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Update a lesson by ID using PATCH method",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=LessonSerializer,
        responses={
            200: openapi.Response(
                'Success: Ok',
                LessonResponseSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def patch(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)

            serializer = LessonSerializer(lesson, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save()

            cache.clear()  # Invalidate cache as database updated

            return Response(
                LessonResponseSerializer(lesson).data,
                status=status.HTTP_200_OK
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
        
        except IntegrityError as e:
            return Response(
                {"detail": "Duplicate lesson title found within the same subject."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LessonDetailView.patch(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # Delete a lesson by ID
    @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Delete a lesson by ID",
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to delete",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            204: 'Success: No Content',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def delete(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            lesson.delete()

            cache.clear()  # Invalidate cache as database updated
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in LessonDetailView.delete(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
