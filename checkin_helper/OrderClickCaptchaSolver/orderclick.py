import os

from OrderClickCaptchaSolver.siamese import Siamese_PT
from OrderClickCaptchaSolver.yolo import YOLO_PT
from OrderClickCaptchaSolver.utils import matchingMode
import OrderClickCaptchaSolver.utils.utils as utils

class OrderClick(object):
    def __init__(self, base_path, siamese_path, yolo_path):
        siamese_path = os.path.join(base_path, siamese_path)
        yolo_path = os.path.join(base_path, yolo_path)
        self.yolo = YOLO_PT(yolo_path, classes=['char', 'target'])
        self.siamese = Siamese_PT(siamese_path)

    def run(self, image_path):
        img = utils.open_image(image_path)
        data = self.yolo.detect(image_path)
        # 需要选择的字
        targets = [i.get("crop") for i in data if i.get("classes") == "target"]
        chars = [i.get("crop") for i in data if i.get("classes") == "char"]
        # 根据坐标进行排序
        chars.sort(key=lambda x: x[0])
        chars = [img.crop(char) for char in chars]
        img_targets = [img.crop(target) for target in targets]
        slys = [self.siamese.detect_images(img_char, img_targets) for img_char in chars]
        sorted_result = matchingMode.find_overall_index(slys)
        result = [targets[j] for i, j in sorted_result]
        return result
