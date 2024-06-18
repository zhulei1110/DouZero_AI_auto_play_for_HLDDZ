import cv2
import numpy as np
import os

from helpers.screen_helper import ScreenHelper

dirArr = ["./images/btn/", "./images/other/", "./images/three/", "./images/my/", "./images/play/"]

class ImageLocator:
    def __init__(self):
        self.templateImages = {}
        self.screenHelper = ScreenHelper()
        for dir in dirArr:
            for file in os.listdir(dir):
                arr = file.split(".")
                if arr[1] == "png":
                    imgCV = cv2.imread(dir + file)
                    self.templateImages.update({arr[0]: imgCV})

        # print('self.templateImages: ', self.templateImages)

    def get_resize_scale(self, image=None):
        if image is None:
            screenshot, _ = self.screenHelper.getScreenshot()
            image = np.asarray(screenshot)

        window_w, window_h = image.shape[1], image.shape[0]
        scale_w = window_w / float(1920)
        scale_h = window_h / float(1080)
        scale = min(scale_w, scale_h)
        return scale
    
    def compute_image_unique_key(self, image):
        image_bytes = image.tobytes()
        hash_value = hash(image_bytes)
        return hash_value

    # 查找所有匹配位置，返回所有坐标的列表
    def locate_all_match_on_image(self, image, template, templateName=None, region=None, scale=None, confidence=0.8):
        if scale is None:
            scale = self.get_resize_scale(image)

        if region is not None:
            x, y, w, h = region
            image = image[y:y + h, x:x + w]

            # 图片日志
            # imageKey = self.compute_image_unique_key(image)
            # regionText = str(region).replace(' ', '').replace(',', '-')
            # cv2.imwrite(f'screenshots/logs/LAM_{templateName}_{regionText}_{imageKey}.png', image)

        image_w, image_h = image.shape[1], image.shape[0]
        template = cv2.resize(template, None, fx=scale, fy=scale)

        # 图片日志
        # templateKey = self.compute_image_unique_key(template)
        # scaleText = f"{scale:.{4}f}".replace('.', '-')
        # cv2.imwrite(f'screenshots/logs/LAM_{templateName}_{regionText}_{scaleText}_{templateKey}.png', template)

        # 使用 OpenCV 的 matchTemplate 函数在 image 中搜索 template
        # cv2.TM_CCOEFF_NORMED 是一种匹配方法，返回一个结果矩阵 res，其中每个值表示模板与图像对应位置的匹配程度
        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

        # 找出结果矩阵中所有大于等于 confidence 的位置，表示这些位置的模板匹配度高于或等于置信度阈值
        loc = np.where(res >= confidence)
        # print('loc: ', loc)

        # 创建一个空列表 points 用于存储匹配位置
        points = []

        # zip(*loc[::-1]) 对找到的匹配位置进行迭代
        for pt in zip(*loc[::-1]):
            # 对于每个匹配位置 pt，将其左上角坐标 (pt[0], pt[1]) 和图像尺寸 (w, h) 添加到 points 列表中
            points.append((pt[0], pt[1], image_w, image_h))

        # print('points: ', points)
        return points

    # 只查找第一个匹配位置，返回单个坐标或 None
    def locate_first_match_on_image(self, image, template, templateName=None, region=None, scale=None, confidence=0.8):
        if scale is None:
            scale = self.get_resize_scale(image)

        if region is not None:
            x, y, w, h = region
            image = image[y:y + h, x:x + w, :]

            # 图片日志
            # imageKey = self.compute_image_unique_key(image)
            # regionText = str(region).replace(' ', '').replace(',', '-')
            # cv2.imwrite(f'screenshots/logs/LFM_{templateName}_{regionText}_{imageKey}.png', image)

        template = cv2.resize(template, None, fx=scale, fy=scale)

        # 图片日志
        # templateKey = self.compute_image_unique_key(template)
        # scaleText = f"{scale:.{4}f}".replace('.', '-')
        # cv2.imwrite(f'screenshots/logs/LFM_{templateName}_{regionText}_{scaleText}_{templateKey}.png', template)

        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        # print(res)
        
        # 查找最佳匹配位置
        # 使用 cv2.minMaxLoc 函数查找匹配结果矩阵 res 中的最大值及其位置。
        # maxLoc 是最大值的位置，即模板在图像中最佳匹配的位置。
        _, _, _, maxLoc = cv2.minMaxLoc(res)

        # 检查匹配置信度
        # res 中是否存在任何值大于或等于置信度阈值 confidence。如果存在，则返回模板匹配的位置。
        if (res >= confidence).any():
            return region[0] + maxLoc[0], region[1] + maxLoc[1]
        else:
            return None

    def locate_match_on_screen(self, templateName, region, scale=None, confidence=0.8, image=None):
        if image is not None:
            screenshot = image
        else:
            screenshot, position = self.screenHelper.getScreenshot()
            # print('image: ', image)
            # print('position: ', position)
        
        # 将 PIL 格式图像转换为 OpenCV 格式（BGR）
        imgcv = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)

        # 调用 LocateOnImage 函数在图像中查找模板图像的位置
        result = self.locate_first_match_on_image(image=imgcv, template=self.templateImages[templateName], templateName=templateName, region=region, scale=scale, confidence=confidence)
        return result