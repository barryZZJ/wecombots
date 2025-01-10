from __future__ import annotations

from io import BytesIO
import ddddocr
import base64
from PIL import Image

ocr: ddddocr.DdddOcr = None

def init_ocr():
    global ocr
    ocr = ddddocr.DdddOcr()

def fuckcaptcha(img: str|bytes|Image.Image, char_range: int|str=6) -> str:
    if char_range is not None:
        ocr.set_ranges(char_range)
        result = ocr.classification(img, probability=True)
        captcha = ''
        for i in result['probability']:
            captcha += result['charsets'][i.index(max(i))]
        return captcha
    return ocr.classification(img)

def dataurl_to_img(data_url):
    base64_str = data_url.split(',')[1]
    # Decode the base64 string to bytes
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_bytes))
    return img

def get_threshold_color(img: Image.Image, total_pixels, percent, reverse=False) -> int:
    """
    Get top n% darkest pixels' color threshold.
    0 represents black, and 255 represents white.
    If reverse=True, get top n% lightest pixels' color threshold.
    :return: threshold pixel color
    """
    colors = img.getcolors()
    if reverse:
        colors = colors[::-1]
    cumsum = 0
    for color, count in colors:
        cumsum += count
        if cumsum >= total_pixels * percent:
            return color
    return colors[-1][0]

if __name__ == '__main__':
    img = Image.open(r"C:\Users\85046\Desktop\16-25-25.png")
    print(fuckcaptcha(img))