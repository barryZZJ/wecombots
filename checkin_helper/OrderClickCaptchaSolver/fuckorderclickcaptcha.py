import os
from PIL import Image

from OrderClickCaptchaSolver.orderclick import OrderClick

oc = OrderClick(os.path.join(os.path.dirname(__file__), 'models'), 'siamese_best_epoch_weights.pth', 'yolo_best.pt')

def fuck_orderclick_captcha(img: Image.Image) -> list[tuple[int, int]]:
    # import random
    # width, height = img.size
    # results = [(random.randint(0, width - 1), random.randint(0, height - 1)) for _ in range(3)]
    # return results
    coords = oc.run(img)
    return coords
