from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Get the default DRF error response
    response = exception_handler(exc, context)

    if response is not None:
        # Extract the existing data (e.g., {"detail": "...", "field": ["error"]})
        data = response.data

        # Wrap into your unified format
        wrapped_response = {
            "detail": data['detail']  # keep the original details for debugging and frontend mapping
        }

        return Response(wrapped_response, status=response.status_code)

    return response