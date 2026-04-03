import io
from PIL import Image
from typing import Tuple

class MediaTool:
    def __init__(self, CutBlockSize=(64,48), BlockZipSize = 1000 , HCutNumMax = 15, LCutNumMax=15):
        self.CutBlockSize = CutBlockSize
        self.BlockZipSize = BlockZipSize # 30000 - 30KByte; 1000 - 1KByte
        self.HCutNumMax = HCutNumMax  # 一张照片最多切15行
        self.LCutNumMax = LCutNumMax  # 一张照片每行最多切15列
        
    def ImgZipToBytes(self, rgb_img, target_size_bytes, max_iterations=50)->bytes:
        # 初始化压缩质量，从90开始（通常JPEG质量范围是0-100）
        quality = 90
        # 迭代尝试不同的压缩质量
        for _ in range(max_iterations):
            # 使用BytesIO作为内存中的文件对象
            buf = io.BytesIO()
            # 保存图片到BytesIO对象，设置JPEG压缩质量
            rgb_img.save(buf, format="JPEG", quality=quality, optimize=True)
            # 获取文件大小
            file_size = buf.getbuffer().nbytes
            # 如果文件大小小于或等于目标大小，则保存并退出循环
            if file_size <= target_size_bytes:
                # 将BytesIO对象中的数据写入到实际文件中
                # with open(input_image_path.replace('.jpg', '_limited.jpg'), 'wb') as f:
                #     f.write(buf.getvalue())
                return buf.getvalue()
            # 如果文件大小仍然太大，则降低压缩质量
            quality -= 2  # 每次迭代降低5点质量
            # 检查是否达到了最低质量限制
            if quality < 1:
                break
        print("Cannot reduce file size below the target while maintaining quality.")
        return None

    def BytesUnZipToImg(self, ImgBytes)->Image:
        if ImgBytes is None:
            return None
        try:
            # 使用BytesIO将字节数据转换为类似文件的对象
            img_io = io.BytesIO(ImgBytes)
            # 使用PIL Image.open从BytesIO对象中读取图片
            RgbImg = Image.open(img_io)
            return RgbImg
        except Exception as e:  # 使用通用Exception来捕获所有异常
            print(f"发生错误: {e}")
            return None

    def PacketImgBlock(self, RgbImg:Image, CutBlockSize=None, BlockZipSize = None)->dict:
        ImgBlock = {}
        width, height = RgbImg.size # 640 480 
        if CutBlockSize is None:
            CutBlockSize = self.CutBlockSize 
        if BlockZipSize is None:
            BlockZipSize = self.BlockZipSize 
        # print("PacketImgBlock", CutBlockSize, BlockZipSize)
        # 计算行和列个数
        if width < CutBlockSize[0] or height < CutBlockSize[1]:
            print("Error:ImgTool 图片尺寸小于块尺寸")
            return None
        LNum = width//CutBlockSize[0]  # 行个数,共HNum行
        HNum = height//CutBlockSize[1] # 列个数,一行有LNum个
        # print("img size:",width, height, "cutNum:",HNum,LNum)
        id = 0
        for i in range(HNum):
            id = i*self.LCutNumMax # 行开头ID
            if i >= self.HCutNumMax:
                break
            for j in range(LNum):
                if j >= self.LCutNumMax:
                    continue
                LeftTopX = CutBlockSize[0]*j
                LeftTopY = CutBlockSize[1]*i
                RightBtmX = LeftTopX + CutBlockSize[0]
                RightBtmy = LeftTopY + CutBlockSize[1]
                CutImg = RgbImg.crop((LeftTopX, LeftTopY, RightBtmX, RightBtmy))
                ImgBytes = self.ImgZipToBytes(CutImg, BlockZipSize)
                ImgBlock[id] = ImgBytes
                # testpos = self.IdToXY(id)
                #if testpos[0] != LeftTopX or testpos[1] != LeftTopY:
                # print("msg:ImgTool", id, testpos, LeftTopX,LeftTopY)
                id += 1
        return ImgBlock

    def UnPackImgBlock(self, RgbImgBlock:dict, NImage = None)->Image:
        if NImage is None:
            return False
        try:
            for Id,val in RgbImgBlock.items():
                block = self.BytesUnZipToImg(val)
                if block is None:
                    continue
                X = (Id % self.LCutNumMax )* self.CutBlockSize[0] #列号*一列的宽度
                Y = (Id // self.LCutNumMax) * self.CutBlockSize[1]  # 行号*一行的高度
                print(Id,X,Y,len(val))
                NImage.paste(block, (X, Y))
            return True
        except Exception as e:  # 使用通用Exception来捕获所有异常
            print(f"发生错误: {e}")
            return False
    
    def IdToXY(self, Id:int, CutBlockSize = None)->Tuple[int, int]:
        if CutBlockSize is None or len(CutBlockSize) != 2:
            CutBlockSize = self.CutBlockSize
        X = (Id % self.LCutNumMax )* CutBlockSize[0] #列号*一列的宽度
        Y = (Id // self.LCutNumMax) * CutBlockSize[1]  # 行号*一行的高度
        return (X, Y)
    