import cv2
import numpy as np

class ColorClassifier(object):
    def __init__(self, debug=True):
        self.debug = debug
        # 颜色范围，主要参考 HSV 颜色分量分布表：
        # 其中，gray 和 white 进行了平衡中线调整，使白色占比更大些
        self.hsv_color = {
            "Gray": [(0, 180), (0, 43), (46, 150)],
            "White": [(0, 180), (0, 30), (151, 255)],
            "Red": [[(0, 10), (160, 180)], (43, 255), (46, 255)],
            "Orange": [(11, 25), (43, 255), (46, 255)],
            "Green": [(35, 77), (43, 255), (46, 255)],
            "Blue": [(100, 124), (43, 255), (46, 255)],
        }
    
    def get_hsv_hist(self, img_hsv, mask=None):
        h, s, v = img_hsv[:, :, 0], img_hsv[:, :, 1], img_hsv[:, :, 2]
        if mask is not None:
            h = h[mask]
            s = s[mask]
            v = v[mask]

        h_bins = [0, 11, 26, 35, 78, 100, 125, 156, 180]
        h_hist = np.histogram(h, h_bins)
        s_bins = [0, 30, 43, 255]
        s_hist = np.histogram(s, s_bins)
        v_bins = [0, 46, 151, 255]
        v_hist = np.histogram(v, v_bins)

        return [h_hist, s_hist, v_hist]

    def get_hsv_info(self, h_hist, s_hist, v_hist):
        infos = {
            "h": {
                "hist": h_hist,
                "argsort": None,
                "sort_normal": None,
                "arg_values": [],
            },
            "s": {
                "hist": s_hist,
                "argsort": None,
                "sort_normal": None,
                "arg_values": [],
            },
            "v": {
                "hist": v_hist,
                "argsort": None,
                "sort_normal": None,
                "arg_values": [],
            }
        }

        for k in infos:
            hist = infos[k]['hist']
            argsort = np.argsort(hist[0])[::-1][:2]  # 逆序排列, 取前面最大的两个
            infos[k]['argsort'] = argsort
            infos[k]['sort_normal'] = hist[0][argsort] / (sum(hist[0]) * 3)
            for idx in argsort:
                value_mean = round(np.mean([hist[1][idx], hist[1][idx + 1]]))
                infos[k]['arg_values'].append(value_mean)

        return infos

    def hsv2color(self, infos):
        h_info = infos['h']
        s_info = infos['s']
        v_info = infos['v']
        result = {}

        for snh, avh in zip(h_info['sort_normal'], h_info['arg_values']):
            for sns, avs in zip(s_info['sort_normal'], s_info['arg_values']):
                for snv, avv in zip(v_info['sort_normal'], v_info['arg_values']):
                    cls = self.hsv2color_one(avh, avs, avv)
                    if cls is None:
                        continue
                    score = snh + sns + snv
                    if cls in result.keys():
                        result[cls] = max(score, result[cls])
                    else:
                        result[cls] = score

        return sorted(result.items(), key=lambda kv: (kv[1], kv[0]))[::-1]

    def hsv2color_one(self, h_mean, s_mean, v_mean):
        for cls, value in self.hsv_color.items():
            if isinstance(value[0], list):
                h_flag = value[0][0][0] <= h_mean <= value[0][0][1] or value[0][1][0] <= h_mean <= value[0][1][1]
            else:
                h_flag = value[0][0] <= h_mean <= value[0][1]
            s_flag = value[1][0] <= s_mean <= value[1][1]
            v_flag = value[2][0] <= v_mean <= value[2][1]
            if h_flag and s_flag and v_flag:
                return cls

        return None

    def classify(self, img):
        if img.shape[2] == 4:
            # If the image has an alpha channel, create a mask to ignore transparent pixels
            alpha_channel = img[:, :, 3]
            mask = alpha_channel > 0
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            mask = None

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h_hist, s_hist, v_hist = self.get_hsv_hist(img_hsv, mask)

        infos = self.get_hsv_info(h_hist, s_hist, v_hist)
        return self.hsv2color(infos)
    
if __name__ == "__main__":
    classifier = ColorClassifier(debug=True)
    image = cv2.imread("images/my-A.png", cv2.IMREAD_UNCHANGED)

    result = classifier.classify(image)
    print(result)

    for cls, score in result:
        print(cls, score)
        if cls == "Red":
            print(score)
