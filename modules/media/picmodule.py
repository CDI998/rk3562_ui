import cv2
import numpy as np
from modules.datamodule.picdatabean import PicDataBean
from tool.globals.pathutils import PathUtils
from PyQt5.QtGui import QImage
import os

class PicModule():
    def __init__(self, LocalPicPath):
        self.PicDataBean = PicDataBean()
        self.LocalPicPath = PathUtils.get_absolute_path(LocalPicPath)
        self.LoadLocalMsg()

    def LoadLocalMsg(self):
        if PathUtils.check_path_exists(self.LocalPicPath):
            print("本地图片路径有效")
            pic_list = PathUtils.get_files_by_type(self.LocalPicPath, "jpg") 
            print(f"本地图片列表: {pic_list}")
            self.PicDataBean.set_local_pic_list(pic_list)
        else:
            print(f"本地图片路径无效: {self.LocalPicPath}")
            
    def switchLocalPic(self, IsUpOption: bool = True) -> str:
        """
        切换本地图片，返回完整的图片路径
        :param IsUpOption: True=切换下一张，False=切换上一张
        :return: 完整的图片路径（str）/路径无效返回空字符串
        """
        # 1. 获取当前图片名称和目标文件名
        curr_name = self.PicDataBean.get_curr_local_pic_name()
        if IsUpOption:
            print(f"当前图片: {curr_name} → 切换到下一张图片")
            new_name = self.PicDataBean.get_next_pic_name(curr_name)
            print(f"切换到下一张图片: {new_name}")
        else:
            print(f"当前图片: {curr_name} → 切换到上一张图片")
            new_name = self.PicDataBean.get_prev_pic_name(curr_name)
            print(f"切换到上一张图片: {new_name}")

        # 2. 校验文件名有效性
        if not new_name:  # 空字符串（列表为空）
            return ""
        new_path = PathUtils.get_absolute_path(self.LocalPicPath+'/'+new_name)
        if PathUtils.check_path_exists(new_path):
            self.PicDataBean.set_curr_local_pic_name(new_name)  # 更新当前图片名称
            return new_path
        else:
            print(f"图片路径无效: {new_path}")
            return ""
    
    def CutJpgImg2JpgBlocks(jpgimage_path: str, x_blocks: int, y_blocks: int):
        """
        将 JPEG 切割成 x*y 块，返回 编号+图片二进制数据
        行ID规则：第1行=0，第2行=10，第3行=20 ... 最大10行
        每行最多10块，最多10行
        返回：列表 [ {"id": 编号, "data": 图片编码数据}, ... ]
        """
        try:
            result = []
            x_blocks = max(1, min(x_blocks, 10))
            y_blocks = max(1, min(y_blocks, 10))
            img = cv2.imread(jpgimage_path)
            if img is None:
                print(f"[错误] 无法读取图片：{jpgimage_path}")
                return result
            h, w = img.shape[:2]
            block_w = w // x_blocks
            block_h = h // y_blocks
            
            for y in range(y_blocks):
                # 行起始ID：0,10,20,30...
                row_start_id = y * 10
                for x in range(x_blocks):
                    current_id = row_start_id + x
                    # 裁剪坐标
                    x1 = x * block_w
                    y1 = y * block_h
                    x2 = x1 + block_w
                    y2 = y1 + block_h
                    # 裁剪块
                    block = img[y1:y2, x1:x2]
                    # 编码为 JPG 二进制
                    _, encoded = cv2.imencode(".jpg", block)
                    block_data = encoded.tobytes()
                    result.append({
                        "id": current_id,
                        "data": block_data
                    })
            return result
        # 所有异常都捕获，返回空列表，不抛错
        except Exception as e:
            print(f"[异常] 图片切块失败：{str(e)}")
            return []


    def CutRgbImg2JpgBlocks(rgb_image: np.ndarray, x_blocks: int, y_blocks: int):
        """
        将 RGB 图像切割成 x*y 块，返回 编号+图片二进制数据
        行ID规则：第1行=0，第2行=10，第3行=20 ... 最大10行
        每行最多10块，最多10行
        :param rgb_image: 输入 RGB 格式图像 (numpy array)
        :param x_blocks: 横向块数
        :param y_blocks: 纵向块数
        :return: 列表 [ {"id": 编号, "data": 图片编码数据}, ... ]
        """
        # 限制最大 10x10
        x_blocks = max(1, min(x_blocks, 10))
        y_blocks = max(1, min(y_blocks, 10))
        # 检查输入是否有效
        if rgb_image is None or len(rgb_image.shape) != 3:
            raise ValueError("输入无效，请传入 RGB 格式的图像数据")
        h, w = rgb_image.shape[:2]
        block_w = w // x_blocks
        block_h = h // y_blocks
        result = []

        for y in range(y_blocks):
            # 行起始ID：0,10,20...
            row_start_id = y * 10
            for x in range(x_blocks):
                current_id = row_start_id + x
                # 裁剪坐标
                x1 = x * block_w
                y1 = y * block_h
                x2 = x1 + block_w
                y2 = y1 + block_h
                # 裁剪块
                block = rgb_image[y1:y2, x1:x2]
                # RGB → BGR（OpenCV 必须转）
                block_bgr = cv2.cvtColor(block, cv2.COLOR_RGB2BGR)
                # 编码为 JPG 二进制
                _, encoded = cv2.imencode(".jpg", block_bgr)
                block_data = encoded.tobytes()

                result.append({
                    "id": current_id,
                    "data": block_data
                })

        return result

    def PasteJpegBlock2RgbImg(
                                target_rgb_img: np.ndarray,
                                block: dict,
                                total_x_blocks: int,
                                total_y_blocks: int
                            ) -> np.ndarray:
        """
        把一个块（id+data）贴到【RGB 目标图片】的正确位置
        :param target_rgb_img: 目标图片（RGB 格式）
        :param block: {"id": 编号, "data": jpeg 二进制数据}
        :param total_x_blocks: 总列数
        :param total_y_blocks: 总行数
        :return: 贴好后的 RGB 图片
        """
        try:
            block_id = block["id"]
            data = block["data"]

            if data is None or len(data) == 0:
                print("[PasteJpegBlock2RgbImg] empty jpeg block data")
                return None

            # 解码 jpeg 数据 → OpenCV 默认是 BGR
            block_data = np.frombuffer(data, dtype=np.uint8).copy()
            block_bgr = cv2.imdecode(block_data, cv2.IMREAD_COLOR)
            if block_bgr is None:
                print("[PasteJpegBlock2RgbImg] jpeg decode failed")
                return None
            
            #  转成 RGB 格式，和目标图一致
            block_rgb = cv2.cvtColor(block_bgr, cv2.COLOR_BGR2RGB)

            # 获取尺寸
            h, w = target_rgb_img.shape[:2]
            block_w = w // total_x_blocks
            block_h = h // total_y_blocks

            # 计算坐标（你的规则：行=ID//10，列=ID%10）
            y = block_id // 10
            x = block_id % 10
            x1 = x * block_w
            y1 = y * block_h

            # 粘贴块（RGB → RGB，完全匹配）
            target_rgb_img[y1:y1+block_h, x1:x1+block_w] = block_rgb

            return target_rgb_img
        except Exception as e:
                print(f"[PasteJpegBlock2RgbImg] exception: {e}")
                return None
                
    def LoadQImageFromPath(self, picpath: str) -> QImage:
        """
        根据本地图片路径加载 QImage
        :param picpath: 图片完整路径
        :return: 加载成功返回 QImage，失败返回空 QImage
        """
        if not picpath:
            print("[LoadQImageFromPath] 图片路径为空")
            return QImage()

        if not os.path.exists(picpath):
            print(f"[LoadQImageFromPath] 图片路径不存在: {picpath}")
            return QImage()

        qimg = QImage(picpath)
        if qimg.isNull():
            print(f"[LoadQImageFromPath] 图片加载失败或格式不支持: {picpath}")
            return QImage()

        return qimg.copy()
