
class VdoDataBean:
    def __init__(self):
        self.video_path = ""    # 本地视频路径

    def set_video_path(self, path):
        self.video_path = path

    def get_video_path(self):
        return self.video_path
