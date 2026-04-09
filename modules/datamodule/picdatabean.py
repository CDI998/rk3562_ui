

class PicDataBean:
    def __init__(self):
        self.image_rgb = None   # RGB图片
        self.image_path = ""    # 本地图片路径
        self.local_pic_list = []   # 本地图片列表
        self.curr_local_pic_name = ""  # 当前正在操作的本地图片名称

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

    def set_local_pic_list(self, pic_list):
        self.local_pic_list = pic_list.copy()

    def get_local_pic_list(self):
        return self.local_pic_list

    def set_image_path(self, path):
        self.image_path = path

    def get_image_path(self):
        return self.image_path
    
    def set_curr_local_pic_name(self, name):
        self.curr_local_pic_name = name
    
    def get_curr_local_pic_name(self):
        return self.curr_local_pic_name
    
    def get_next_pic_name(self, curr_name):
        if not self.local_pic_list:
            return ""
        if curr_name not in self.local_pic_list:
            return self.local_pic_list[0]
        curr_index = self.local_pic_list.index(curr_name)
        next_index = (curr_index + 1) % len(self.local_pic_list)
        return self.local_pic_list[next_index]

    def get_prev_pic_name(self, curr_name):
        if not self.local_pic_list:
            return ""
        if curr_name not in self.local_pic_list:
            return self.local_pic_list[-1]
        curr_index = self.local_pic_list.index(curr_name)
        prev_index = (curr_index - 1) % len(self.local_pic_list)
        return self.local_pic_list[prev_index]