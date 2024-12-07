from __future__ import annotations

from io import BytesIO
import ddddocr
import base64
from PIL import Image

ocr = ddddocr.DdddOcr()

def fuckcaptcha(img: str|bytes|Image.Image):
    return ocr.classification(img)

def dataurl_to_img(data_url):
    base64_str = data_url.split(',')[1]
    # Decode the base64 string to bytes
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_bytes))
    return img
