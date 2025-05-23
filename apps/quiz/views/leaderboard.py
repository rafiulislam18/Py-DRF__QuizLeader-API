from django.db.models import Max, Avg, Count, F

from .base import *
from ..models import Subject, QuizAttempt
from ..paginators import (
    SubjectLeaderboardPagination,
    GlobalLeaderboardPagination
)
from ..serializers import (
    LeaderboardResponseSerializer,
    LeaderboardPaginatedResponseSerializer
)


class SubjectLeaderboardView(APIView):
    permission_classes = [AllowAny]
    pagination_class = SubjectLeaderboardPagination

    def get_cache_key(self, subject_id, page_number, page_size):
        return f'leaderboard:subject:{subject_id}:page:{page_number}:size:{page_size}'

    # Get subject-specific leaderboard (top 10)
    @swagger_auto_schema(
        tags=["Quiz-Leaderboard"],
        operation_id="quiz_subject_leaderboard",
        operation_description="Get subject-specific leaderboard (top 10 players)",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject",
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
                    f"Number of results per page (default: {SubjectLeaderboardPagination.page_size}, "
                    f"max: {SubjectLeaderboardPagination.max_page_size})"
                ),
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                LeaderboardPaginatedResponseSerializer
            ),
            400: 'Error: Bad request',
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

            cache_key = self.get_cache_key(subject_id, page_number, page_size)  # Unique key for caching leaderboard data
            leaderboard_data = cache.get(cache_key)  # Try getting cached data

            if not leaderboard_data:
                leaderboard_data = QuizAttempt.objects.filter(
                    lesson__subject=subject,  # Filter by subject through lesson
                    completed=True
                ).values(username=F('user__username')).annotate(
                    high_score=Max('score'),
                    avg_score=Avg('score'),
                    total_played=Count('id')
                ).order_by('-high_score')[:10]

                cache.set(cache_key, leaderboard_data, timeout=60)  # Cache for 1 minute

            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(leaderboard_data, request)
            if page is not None:
                serializer = LeaderboardResponseSerializer(page, many=True)
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
                f"Error in SubjectLeaderboardView.get(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GlobalLeaderboardView(APIView):
    permission_classes = [AllowAny]
    pagination_class = GlobalLeaderboardPagination

    def get_cache_key(self, page_number, page_size):
        return f'leaderboard:global:page:{page_number}:size:{page_size}'

    # Get global leaderboard (top 25) accross all lessons
    @swagger_auto_schema(
        tags=["Quiz-Leaderboard"],
        operation_id="quiz_leaderboard",
        operation_description=(
            "Get global leaderboard (top 25 players) across all lessons"
        ),
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
                description=(
                    f"Number of results per page (default: {GlobalLeaderboardPagination.page_size}, "
                    f"max: {GlobalLeaderboardPagination.max_page_size})"
                ),
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                LeaderboardPaginatedResponseSerializer
            ),
            400: 'Error: Bad request',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request):
        try:
            # Get current page from request
            page_number = request.query_params.get('page', 1)

            # Get page size from request, default to the pagination class default
            page_size = request.query_params.get(
                'page_size',
                self.pagination_class.page_size
            )

            cache_key = self.get_cache_key(page_number, page_size)  # Unique key for caching leaderboard data
            leaderboard_data = cache.get(cache_key)  # Try getting cached data

            if not leaderboard_data:
                leaderboard_data = QuizAttempt.objects.filter(
                    completed=True
                ).values(username=F('user__username')).annotate(
                    high_score=Max('score'),
                    avg_score=Avg('score'),
                    total_played=Count('id')
                ).order_by('-high_score')[:25]

                cache.set(cache_key, leaderboard_data, timeout=60)  # Cache for 1 minute

            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(leaderboard_data, request)
            if page is not None:
                serializer = LeaderboardResponseSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            # If paginaation is not applied, throw an error
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
                f"Error in GlobalLeaderboardView.get(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
