# Background Removal Utility

This utility provides background removal functionality for images using AI models.

## Installation

Install the required dependencies:

```bash
pip install rembg onnxruntime
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Standalone Script

Use the standalone script to process images from the command line:

```bash
python utils/standalone_script.py input.jpg output.png
```

If no output path is provided, it will create `input_no_bg.png`:

```bash
python utils/standalone_script.py photo.jpg
```

### 2. Python API

Import and use the utility functions:

```python
from utils.background_removal import remove_background_from_image, remove_background_from_pil_image

# From file path
remove_background_from_image(
    image_path="input.jpg",
    output_path="output.png"
)

# From bytes
with open("input.jpg", "rb") as f:
    image_bytes = f.read()

output_bytes = remove_background_from_image(
    image_bytes=image_bytes,
    return_bytes=True
)

# From PIL Image
from PIL import Image
pil_image = Image.open("input.jpg")
processed_image = remove_background_from_pil_image(pil_image)
processed_image.save("output.png")
```

### 3. Django REST API Endpoint

The utility includes a REST API endpoint for background removal:

**Endpoint:** `POST /api/v1/utils/remove-background/`

**Authentication:** Required (JWT token)

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
    "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "success": true,
    "mime_type": "image/png"
}
```

**Example using curl:**
```bash
curl -X POST \
  http://localhost:8000/api/v1/utils/remove-background/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@photo.jpg"
```

**Example using JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/v1/utils/remove-background/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const data = await response.json();
if (data.success) {
  // Use data.image (base64 data URL) directly in img src
  document.getElementById('preview').src = data.image;
}
```

## Features

- ✅ AI-powered background removal using `rembg` library
- ✅ Supports multiple input formats (JPEG, PNG, etc.)
- ✅ Always outputs PNG with transparent background
- ✅ Can process from file paths, bytes, or PIL Images
- ✅ REST API endpoint for easy integration
- ✅ Returns base64 encoded images for frontend use

## Notes

- The first time you run `rembg`, it will download the AI model (~170MB)
- Processing time depends on image size and system performance
- Output images are always in PNG format with alpha channel (transparent background)
- The API endpoint requires authentication (JWT token)

