from ultralytics import YOLO
import numpy as np
from PIL import Image
from io import BytesIO

class YOLO_PT:
    def __init__(self, pt_path, classes):
        self.model=YOLO(pt_path)
        self.classes=classes

    def detect(self, file):
        # 图片转换为矩阵
        if isinstance(file, np.ndarray):
            img = Image.fromarray(file)
        elif isinstance(file, bytes):
            img = Image.open(BytesIO(file))
        elif isinstance(file, Image.Image):
            img = file
        else:
            img = Image.open(file)
        img = img.convert('RGB')
        img = np.array(img)
        data = self.model(file, classes=list(range(len(self.classes))))[0].cpu().numpy()
        pred = self._get_pred(data, conf_thres=0.5)
        res = tag_images(img, pred, self.classes, 0.5)
        return res

    def _get_pred(self, data, conf_thres=0.5):
        boxes = data.boxes
        boxes = boxes[boxes.conf > conf_thres]  # Filter boxes by confidence
        boxes = boxes[(-boxes.conf).argsort()]  # Sort boxes by confidence in descending order

        pred = [np.hstack((boxes.xyxy, boxes.conf[:, None], boxes.cls[:, None]))]
        return pred

    def infer(self, img_path):
        self.model(img_path, save=True, save_crop=True)


def tag_images(imgs, img_detections, classes, max_prob=0.5):
    imgs = [imgs]

    """图片展示"""
    results = []
    zero = lambda x: int(x) if x > 0 else 0
    if img_detections is None:
        return results

    for img_i, (img, detections) in enumerate(zip(imgs, img_detections)):
        # Create plot
        if detections is not None:
            for x1, y1, x2, y2, conf, cls_pred in detections:
                if conf > max_prob:
                    results.append(
                        {
                            "crop": [zero(i) for i in (x1, y1, x2, y2)],
                            "classes": classes[int(cls_pred)],
                            'prob': conf,

                        }
                    )
        else:
            print("识别失败")
    return results