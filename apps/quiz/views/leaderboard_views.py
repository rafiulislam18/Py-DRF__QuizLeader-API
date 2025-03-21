from django.db.models import Max, Avg, Count, F

from .base import *
from ..models import QuizAttempt
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

    # Get subject-specific leaderboard (top 10)
    @swagger_auto_schema(
        tags=["Quiz-Leaderboard"],
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
                'Success: Get subject-specific leaderboard successful',
                LeaderboardPaginatedResponseSerializer
            ),
            400: 'Error: Bad request',
            404: 'Error: Not found',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, subject_id):
        try:
            attempts = QuizAttempt.objects.filter(
                lesson__subject__id=subject_id,  # Filter by subject through lesson
                completed=True
            ).values(username=F('user__username')).annotate(
                high_score=Max('score'),
                avg_score=Avg('score'),
                total_played=Count('id')
            ).order_by('-high_score')[:10]

            if not attempts.exists():
                return Response(
                        {"detail": "No data found for the given subject."},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(attempts, request)
            if page is not None:
                serializer = LeaderboardResponseSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            # If pagination is not applied, throw an error
            return Response(
                {"error": "Pagination is required for this endpoint."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except QuizAttempt.DoesNotExist:
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

    # Get global leaderboard (top 25) accross all lessons
    @swagger_auto_schema(
        tags=["Quiz-Leaderboard"],
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
                'Success: Get global leaderboard successful',
                LeaderboardPaginatedResponseSerializer
            ),
            400: 'Error: Bad request',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request):
        try:
            attempts = QuizAttempt.objects.filter(
                completed=True
            ).values(username=F('user__username')).annotate(
                high_score=Max('score'),
                avg_score=Avg('score'),
                total_played=Count('id')
            ).order_by('-high_score')[:25]

            # Enforce pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(attempts, request)
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
