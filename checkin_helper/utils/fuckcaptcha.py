from __future__ import annotations

from io import BytesIO
import ddddocr
import base64
from PIL import Image

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

if __name__ == '__main__':
    img = Image.open(r'E:\Coding2\PyProjects\wecombots\checkin_helper\modules\captcha/auT.png')
    print(fuckcaptcha(img))