"""
Background removal utility using rembg AI library.
Refer to BACKGROUND_REMOVAL_DOCUMENTATION.md for details.
"""

import io
import os
from typing import Optional

from PIL import Image

# Lazy import prevents startup failures if rembg is not installed
_REMBG_AVAILABLE = None
_REMBG_REMOVE = None


def _get_rembg_remove():
    """Lazy import of rembg.remove function."""
    global _REMBG_AVAILABLE, _REMBG_REMOVE

    if _REMBG_AVAILABLE is None:
        try:
            from rembg import remove

            _REMBG_REMOVE = remove
            _REMBG_AVAILABLE = True
        except ImportError as e:
            _REMBG_AVAILABLE = False
            raise ImportError(
                "rembg library is not installed. "
                "Please install it with: pip install rembg onnxruntime"
            ) from e

    if not _REMBG_AVAILABLE:
        raise ImportError("rembg library is not available")

    return _REMBG_REMOVE


def remove_background_from_image(
    image_path: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    output_path: Optional[str] = None,
    return_bytes: bool = False,
) -> Optional[bytes]:
    """
    Remove background from image. See BACKGROUND_REMOVAL_DOCUMENTATION.md for usage.

    Args:
        image_path: Input image file path (or use image_bytes)
        image_bytes: Image data as bytes (or use image_path)
        output_path: Optional output file path
        return_bytes: Return processed image as bytes

    Returns:
        Processed image bytes if return_bytes=True, else None
    """
    if not image_path and not image_bytes:
        raise ValueError("Either image_path or image_bytes must be provided")

    if image_path:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        with open(image_path, "rb") as f:
            input_data = f.read()
    else:
        input_data = image_bytes

    try:
        remove_func = _get_rembg_remove()
        output_data = remove_func(input_data)
    except ImportError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to remove background: {str(e)}")

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(output_data)

    if return_bytes:
        return output_data

    return None


def remove_background_from_pil_image(pil_image: Image.Image) -> Image.Image:
    """
    Remove background from PIL Image. See BACKGROUND_REMOVAL_DOCUMENTATION.md.

    Args:
        pil_image: PIL Image object

    Returns:
        PIL Image with transparent background (RGBA)
    """
    img_bytes = io.BytesIO()
    pil_image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    remove_func = _get_rembg_remove()
    output_data = remove_func(img_bytes.read())

    return Image.open(io.BytesIO(output_data))


def process_uploaded_image(
    uploaded_file,
    save_path: Optional[str] = None,
    return_base64: bool = False,
):
    """
    Process Django UploadedFile to remove background. See BACKGROUND_REMOVAL_DOCUMENTATION.md.

    Args:
        uploaded_file: Django UploadedFile object
        save_path: Optional output file path
        return_base64: Return base64 encoded string

    Returns:
        Tuple: (bytes, mime_type) or (bytes, mime_type, base64_string) if return_base64=True
    """
    import base64

    uploaded_file.seek(0)
    input_data = uploaded_file.read()

    remove_func = _get_rembg_remove()
    output_data = remove_func(input_data)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(output_data)

    mime_type = "image/png"

    if return_base64:
        base64_data = base64.b64encode(output_data).decode("utf-8")
        return output_data, mime_type, base64_data

    return output_data, mime_type
