import numpy as np
import torch
import torch.backends.cudnn as cudnn
from PIL import Image

from OrderClickCaptchaSolver.nets.siamese import Siamese
from OrderClickCaptchaSolver.utils.utils import letterbox_image, preprocess_input, cvtColor


#---------------------------------------------------#
#   使用自己训练好的模型预测需要修改model_path参数
#---------------------------------------------------#
class Siamese_PT(object):
    #---------------------------------------------------#
    #   初始化Siamese
    #---------------------------------------------------#
    def __init__(self, model_path, input_shape=(105, 105), letterbox_image=False):
        self.model_path = model_path
        self.input_shape = input_shape
        #   该变量用于控制是否使用letterbox_image对输入图像进行不失真的resize
        #   否则对图像进行CenterCrop
        self.letterbox_image = letterbox_image
        self.cuda = torch.cuda.is_available()
        self.generate()
        
    #---------------------------------------------------#
    #   载入模型
    #---------------------------------------------------#
    def generate(self):
        #---------------------------#
        #   载入模型与权值
        #---------------------------#
        print('Loading weights into state dict...')
        device  = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model   = Siamese(self.input_shape)
        model.load_state_dict(torch.load(self.model_path, map_location=device))
        self.net = model.eval()
        print('{} model loaded.'.format(self.model_path))

        if self.cuda:
            self.net = torch.nn.DataParallel(self.net)
            cudnn.benchmark = True
            self.net = self.net.cuda()
    
    #---------------------------------------------------#
    #   检测图片
    #---------------------------------------------------#
    def detect_image(self, image_1: Image.Image, image_2: Image.Image):
        #---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #---------------------------------------------------------#
        image_1 = cvtColor(image_1)
        image_2 = cvtColor(image_2)
        
        #---------------------------------------------------#
        #   对输入图像进行不失真的resize
        #---------------------------------------------------#
        image_1 = letterbox_image(image_1, [self.input_shape[1], self.input_shape[0]], self.letterbox_image)
        image_2 = letterbox_image(image_2, [self.input_shape[1], self.input_shape[0]], self.letterbox_image)
        
        #---------------------------------------------------------#
        #   归一化+添加上batch_size维度
        #---------------------------------------------------------#
        photo_1  = preprocess_input(np.array(image_1, np.float32))
        photo_2  = preprocess_input(np.array(image_2, np.float32))

        with torch.no_grad():
            #---------------------------------------------------#
            #   添加上batch维度，才可以放入网络中预测
            #---------------------------------------------------#
            photo_1 = torch.from_numpy(np.expand_dims(np.transpose(photo_1, (2, 0, 1)), 0)).type(torch.FloatTensor)
            photo_2 = torch.from_numpy(np.expand_dims(np.transpose(photo_2, (2, 0, 1)), 0)).type(torch.FloatTensor)
            
            if self.cuda:
                photo_1 = photo_1.cuda()
                photo_2 = photo_2.cuda()
                
            #---------------------------------------------------#
            #   获得预测结果，output输出为概率
            #---------------------------------------------------#
            output = self.net([photo_1, photo_2])[0]
            output = torch.nn.Sigmoid()(output)

        # plt.subplot(1, 2, 1)
        # plt.imshow(np.array(image_1))
        #
        # plt.subplot(1, 2, 2)
        # plt.imshow(np.array(image_2))
        # plt.text(-12, -12, 'Similarity:%.3f' % output, ha='center', va= 'bottom',fontsize=11)
        # plt.show()
        output = output.cpu().numpy()
        return output

    def detect_images(self, image_1: Image.Image, images_2: list[Image.Image]):
        # ---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        # ---------------------------------------------------------#
        image_1 = cvtColor(image_1)
        images_2 = [cvtColor(image_2) for image_2 in images_2]

        # ---------------------------------------------------#
        #   对输入图像进行不失真的resize
        # ---------------------------------------------------#
        image_1 = letterbox_image(image_1, [self.input_shape[1], self.input_shape[0]], self.letterbox_image)
        images_2 = [letterbox_image(image_2, [self.input_shape[1], self.input_shape[0]], self.letterbox_image) for image_2 in images_2]

        # ---------------------------------------------------------#
        #   归一化+添加上batch_size维度
        # ---------------------------------------------------------#
        photo_1 = preprocess_input(np.array(image_1, np.float32))
        photo_1 = np.expand_dims(np.transpose(photo_1, (2, 0, 1)), 0)  # shape: (1, C, H, W)

        photos_2 = [preprocess_input(np.array(img, np.float32)) for img in images_2]
        photos_2 = np.stack([np.transpose(img, (2, 0, 1)) for img in photos_2], axis=0)  # shape: (N, C, H, W)

        with torch.no_grad():
            photo_1_tensor = torch.from_numpy(np.repeat(photo_1, len(images_2), axis=0)).type(
                torch.FloatTensor)  # (N, C, H, W)
            photos_2_tensor = torch.from_numpy(photos_2).type(torch.FloatTensor)  # (N, C, H, W)

            if self.cuda:
                photo_1_tensor = photo_1_tensor.cuda()
                photos_2_tensor = photos_2_tensor.cuda()

            # 批量预测
            output = self.net([photo_1_tensor, photos_2_tensor]).squeeze()
            output = torch.nn.Sigmoid()(output)
        output = output.cpu().numpy()
        return output