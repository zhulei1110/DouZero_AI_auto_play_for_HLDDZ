import cv2
import collections
import numpy as np

class ColorRecognizer:
    def get_color_dict(self):
        # 定义字典存放颜色分量上下限
        dict = collections.defaultdict(list)

        # 黑色
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 46])
        black_color_list = []
        black_color_list.append(lower_black)
        black_color_list.append(upper_black)
        dict['black'] = black_color_list
    
        # 灰色
        # lower_gray = np.array([0, 0, 46])
        # upper_gray = np.array([180, 43, 220])
        # gray_color_list = []
        # gray_color_list.append(lower_gray)
        # gray_color_list.append(upper_gray)
        # dict['gray'] = gray_color_list
    
        # 白色
        # lower_white = np.array([0, 0, 221])
        # upper_white = np.array([180, 30, 255])
        # white_color_list = []
        # white_color_list.append(lower_white)
        # white_color_list.append(upper_white)
        # dict['white'] = white_color_list
    
        # 红色
        lower_red = np.array([156, 43, 46])
        upper_red = np.array([180, 255, 255])
        red_color_list = []
        red_color_list.append(lower_red)
        red_color_list.append(upper_red)
        dict['red'] = red_color_list
    
        # 红色2
        lower_red = np.array([0, 43, 46])
        upper_red = np.array([10, 255, 255])
        red2_color_list = []
        red2_color_list.append(lower_red)
        red2_color_list.append(upper_red)
        dict['red2'] = red2_color_list
    
        # 橙色
        # lower_orange = np.array([11, 43, 46])
        # upper_orange = np.array([25, 255, 255])
        # orange_color_list = []
        # orange_color_list.append(lower_orange)
        # orange_color_list.append(upper_orange)
        # dict['orange'] = orange_color_list
    
        # 黄色
        # lower_yellow = np.array([26, 43, 46])
        # upper_yellow = np.array([34, 255, 255])
        # yellow_color_list = []
        # yellow_color_list.append(lower_yellow)
        # yellow_color_list.append(upper_yellow)
        # dict['yellow'] = yellow_color_list
    
        # 绿色
        # lower_green = np.array([35, 43, 46])
        # upper_green = np.array([77, 255, 255])
        # green_color_list = []
        # green_color_list.append(lower_green)
        # green_color_list.append(upper_green)
        # dict['green'] = green_color_list
    
        # 青色
        # lower_cyan = np.array([78, 43, 46])
        # upper_cyan = np.array([99, 255, 255])
        # cyan_color_list = []
        # cyan_color_list.append(lower_cyan)
        # cyan_color_list.append(upper_cyan)
        # dict['cyan'] = cyan_color_list
    
        # 蓝色
        # lower_blue = np.array([100, 43, 46])
        # upper_blue = np.array([124, 255, 255])
        # blue_color_list = []
        # blue_color_list.append(lower_blue)
        # blue_color_list.append(upper_blue)
        # dict['blue'] = blue_color_list
    
        # 紫色
        # lower_purple = np.array([125, 43, 46])
        # upper_purple = np.array([155, 255, 255])
        # purple_color_list = []
        # purple_color_list.append(lower_purple)
        # purple_color_list.append(upper_purple)
        # dict['purple'] = purple_color_list
    
        return dict

    def get_color(self, image):
        color = None
        color_dict = self.get_color_dict()

        maxsum = -100
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        for d in color_dict:
            mask = cv2.inRange(hsv, color_dict[d][0], color_dict[d][1])
            binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
            binary = cv2.dilate(binary, None, iterations=2)

            contours = cv2.findContours(binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]

            sum = 0
            for c in contours:
                sum += cv2.contourArea(c)
            
            if sum > maxsum:
                maxsum = sum
                color = d

        return color
    
    def check_image_is_red_or_black(self, image):
        color = self.get_color(image)
        return color
 
if __name__ == '__main__':
    colorRecognizer = ColorRecognizer()
    image = cv2.imread("screenshots/logs/cc_X_2673180423679364024_129-154_328-351_img2.png", cv2.IMREAD_UNCHANGED)
    color = colorRecognizer.check_image_is_red_or_black(image)
    print(color)