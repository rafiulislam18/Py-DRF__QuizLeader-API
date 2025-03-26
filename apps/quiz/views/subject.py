from .base import *
from ..models import Subject
from ..paginators import SubjectListPagination
from ..serializers import (
    SubjectSerializer,
    SubjectPaginatedResponseSerializer
)


class SubjectListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = SubjectListPagination
    
    def get_cache_key(self, page_number, page_size):
        return f'subjects:page:{page_number}:size:{page_size}'

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
                description=(
                    f"Number of results per page (default: {SubjectListPagination.page_size}, "
                    f"max: {SubjectListPagination.max_page_size})"
                ),
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                SubjectPaginatedResponseSerializer
            ),
            400: 'Error: Bad Request',
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
            # Log the error for debugging
            logger.error(
                f"Error in SubjectListCreateView.get(): {str(e)}",
                exc_info=True
            )

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
            201: openapi.Response(
                'Success: Created',
                SubjectSerializer
            ),
            400: 'Error: Bad request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            429: 'Error: Too many requests',
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
            # Log the error for debugging
            logger.error(
                f"Error in SubjectListCreateView.post(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubjectDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    # Get/retrieve a subject by ID
    @swagger_auto_schema(
        tags=["Quiz-Subjects"],
        operation_description="Get/retrieve a subject by ID",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                SubjectSerializer
            ),
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
            return Response(
                SubjectSerializer(subject).data,
                status=status.HTTP_200_OK
            )
        
        except Subject.DoesNotExist:
            return Response(
                {"detail": "Subject not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in SubjectDetailView.get(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Update a subject by ID using PUT method
    @swagger_auto_schema(
        tags=["Quiz-Subjects"],
        operation_description="Update a subject by ID using PUT method",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=SubjectSerializer,
        responses={
            200: openapi.Response(
                'Success: Ok',
                SubjectSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def put(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
            
            serializer = SubjectSerializer(subject, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            cache.clear()  # Invalidate cache as database updated
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
            # Log the error for debugging
            logger.error(
                f"Error in SubjectDetailView.put(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # Update a subject by ID using PATCH method
    @swagger_auto_schema(
        tags=["Quiz-Subjects"],
        operation_description="Update a subject by ID using PATCH method",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=SubjectSerializer,
        responses={
            200: openapi.Response(
                'Success: Ok',
                SubjectSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def patch(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)

            serializer = SubjectSerializer(subject, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            cache.clear()  # Invalidate cache as database updated
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
            # Log the error for debugging
            logger.error(
                f"Error in SubjectDetailView.patch(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # Delete a subject by ID
    @swagger_auto_schema(
        tags=["Quiz-Subjects"],
        operation_description="Delete a subject by ID",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to delete",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            204: 'Success: No content',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def delete(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
            subject.delete()

            cache.clear()  # Invalidate cache as database updated
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Subject.DoesNotExist:
            return Response(
                {"detail": "Subject not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in SubjectDetailView.delete(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
