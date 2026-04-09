

class PicDataBean:
    def __init__(self):
        self.image_rgb = None   # RGB图片
        self.image_path = ""    # 本地图片路径

    # ---------------------
    # 图片 接口
    # ---------------------
    def set_image_rgb(self, img_data):
        if img_data is not None:
            self.image_rgb = img_data.copy()
        else:
            self.image_rgb = None

    def get_image_rgb(self):
        return self.image_rgb
    
    def set_image_path(self, path):
        self.image_path = path

    def get_image_path(self):
        return self.image_path