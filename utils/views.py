"""
Background removal API endpoint.
Refer to BACKGROUND_REMOVAL_DOCUMENTATION.md for API details.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.core.files.uploadedfile import InMemoryUploadedFile
import base64

def get_process_uploaded_image():
    """Lazy import to prevent Django startup failures."""
    try:
        from .background_removal import process_uploaded_image
        return process_uploaded_image
    except ImportError as e:
        raise ImportError(
            "Background removal functionality is not available. "
            "Please install required dependencies: pip install rembg onnxruntime numpy<2.0"
        ) from e


class RemoveBackgroundView(APIView):
    """
    POST /api/v1/utils/remove-background/
    See BACKGROUND_REMOVAL_DOCUMENTATION.md for request/response format.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"error": "No file provided. Please upload an image file.", "success": False},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            
            if not uploaded_file.content_type.startswith('image/'):
                return Response(
                    {"error": "Invalid file type. Please upload an image file.", "success": False},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                process_uploaded_image = get_process_uploaded_image()
            except ImportError as e:
                return Response(
                    {
                        "error": str(e),
                        "success": False,
                        "detail": "Background removal dependencies are not installed."
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            output_data, mime_type, base64_data = process_uploaded_image(
                uploaded_file,
                return_base64=True
            )
            
            data_url = f"data:{mime_type};base64,{base64_data}"
            
            return Response(
                {
                    "image": data_url,
                    "success": True,
                    "mime_type": mime_type
                },
                status=status.HTTP_200_OK
            )
            
        except ImportError as e:
            return Response(
                {
                    "error": f"Background removal service unavailable: {str(e)}",
                    "success": False,
                    "detail": "Please install required dependencies: pip install rembg onnxruntime numpy<2.0"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to process image: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

