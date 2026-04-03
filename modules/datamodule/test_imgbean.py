import pytest
import numpy as np
from PIL import Image
import copy

# 显式导入被测类
from modules.datamodule.ImgBean import ImgBean


class TestImgBeanInit:
    """测试 ImgBean 类的初始化"""

    def test_init_default_values(self):
        """测试初始化后的默认值"""
        bean = ImgBean()
        assert bean.CamFrameRGB is None
        assert bean.QtImgRGB is None
        assert bean.NetImgRGB is None
        assert bean.CurrLocalPicNum == 0
        assert bean.PicList == []


class TestSetCamFrameRGB:
    """测试 SetCamFrameRGB 方法"""

    def test_set_cam_frame_rgb_with_valid_array(self):
        """测试使用有效的numpy数组设置摄像头帧"""
        bean = ImgBean()
        test_frame = np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 0]]], dtype=np.uint8)
        result = bean.SetCamFrameRGB(test_frame)
        assert result is True
        assert bean.CameraFrameRGB is not None
        assert np.array_equal(bean.CameraFrameRGB, test_frame)

    def test_set_cam_frame_rgb_copies_array(self):
        """测试深拷贝：修改原始数组不影响内部存储"""
        bean = ImgBean()
        test_frame = np.array([[[100, 100, 100]]], dtype=np.uint8)
        bean.SetCamFrameRGB(test_frame)
        # 修改原始数组
        test_frame[0, 0, 0] = 0
        # 验证内部数据未被修改
        assert bean.CameraFrameRGB[0, 0, 0] == 100

    def test_set_cam_frame_rgb_with_single_pixel(self):
        """测试单像素数组"""
        bean = ImgBean()
        test_frame = np.array([[[128, 64, 32]]], dtype=np.uint8)
        result = bean.SetCamFrameRGB(test_frame)
        assert result is True
        assert bean.CameraFrameRGB.shape == (1, 1, 3)

    def test_set_cam_frame_rgb_with_large_array(self):
        """测试大尺寸数组"""
        bean = ImgBean()
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = bean.SetCamFrameRGB(test_frame)
        assert result is True
        assert bean.CameraFrameRGB.shape == (480, 640, 3)

    def test_set_cam_frame_rgb_with_grayscale_array(self):
        """测试灰度图像数组（2维）"""
        bean = ImgBean()
        test_frame = np.array([[100, 150], [200, 250]], dtype=np.uint8)
        result = bean.SetCamFrameRGB(test_frame)
        assert result is True

    def test_set_cam_frame_rgb_with_empty_array(self):
        """测试空数组"""
        bean = ImgBean()
        test_frame = np.array([], dtype=np.uint8).reshape(0, 0, 3)
        result = bean.SetCamFrameRGB(test_frame)
        assert result is True
        assert bean.CameraFrameRGB.shape == (0, 0, 3)


class TestGetCamFrameRGB:
    """测试 GetCamFrameRGB 方法"""

    def test_get_cam_frame_rgb_returns_copy(self):
        """测试返回的是深拷贝而非引用"""
        bean = ImgBean()
        test_frame = np.array([[[50, 100, 150]]], dtype=np.uint8)
        bean.SetCamFrameRGB(test_frame)
        retrieved = bean.GetCamFrameRGB()
        # 修改返回的数组
        retrieved[0, 0, 0] = 0
        # 验证内部数据未被修改
        assert bean.CameraFrameRGB[0, 0, 0] == 50

    def test_get_cam_frame_rgb_when_none(self):
        """测试当未设置时返回None"""
        bean = ImgBean()
        result = bean.GetCamFrameRGB()
        assert result is None


class TestSetQtImgRGB:
    """测试 SetQtImgRGB 方法"""

    def test_set_qt_img_rgb_with_valid_image(self):
        """测试使用有效的PIL图像设置Qt图像"""
        bean = ImgBean()
        test_image = Image.new('RGB', (100, 100), color=(255, 0, 0))
        result = bean.SetQtImgRGB(test_image)
        assert result is True
        assert bean.QtImgRGB is not None

    def test_set_qt_img_rgb_copies_image(self):
        """测试深拷贝：修改原始图像不影响内部存储"""
        bean = ImgBean()
        test_image = Image.new('RGB', (50, 50), color=(128, 128, 128))
        bean.SetQtImgRGB(test_image)
        # 修改原始图像
        pixels = test_image.load()
        pixels[0, 0] = (0, 0, 0)
        # 验证内部图像未被修改
        internal_pixels = bean.QtImgRGB.load()
        assert internal_pixels[0, 0] == (128, 128, 128)

    def test_set_qt_img_rgb_with_rgba_image(self):
        """测试RGBA模式图像"""
        bean = ImgBean()
        test_image = Image.new('RGBA', (10, 10), color=(255, 0, 0, 128))
        result = bean.SetQtImgRGB(test_image)
        assert result is True
        assert bean.QtImgRGB.mode == 'RGBA'


class TestGetQtImgRGB:
    """测试 GetQtImgRGB 方法"""

    def test_get_qt_img_rgb_returns_copy(self):
        """测试返回的是深拷贝而非引用"""
        bean = ImgBean()
        test_image = Image.new('RGB', (20, 20), color=(100, 100, 100))
        bean.SetQtImgRGB(test_image)
        retrieved = bean.GetQtImgRGB()
        # 修改返回的图像
        pixels = retrieved.load()
        pixels[0, 0] = (0, 0, 0)
        # 验证内部图像未被修改
        internal_pixels = bean.QtImgRGB.load()
        assert internal_pixels[0, 0] == (100, 100, 100)

    def test_get_qt_img_rgb_when_none(self):
        """测试当未设置时返回深拷贝的None"""
        bean = ImgBean()
        result = bean.GetQtImgRGB()
        assert result is None


class TestSetNetImgRGB:
    """测试 SetNetImgRGB 方法"""

    def test_set_net_img_rgb_with_valid_image(self):
        """测试使用有效的PIL图像设置网络图像"""
        bean = ImgBean()
        test_image = Image.new('RGB', (200, 150), color=(0, 255, 0))
        result = bean.SetNetImgRGB(test_image)
        assert result is True
        assert bean.NetImgRGB is not None

    def test_set_net_img_rgb_copies_image(self):
        """测试深拷贝：修改原始图像不影响内部存储"""
        bean = ImgBean()
        test_image = Image.new('RGB', (30, 30), color=(64, 128, 192))
        bean.SetNetImgRGB(test_image)
        # 修改原始图像
        pixels = test_image.load()
        pixels[0, 0] = (0, 0, 0)
        # 验证内部图像未被修改
        internal_pixels = bean.NetImgRGB.load()
        assert internal_pixels[0, 0] == (64, 128, 192)


class TestGetNetImgRGB:
    """测试 GetNetImgRGB 方法"""

    def test_get_net_img_rgb_returns_copy(self):
        """测试返回的是深拷贝而非引用"""
        bean = ImgBean()
        test_image = Image.new('RGB', (40, 40), color=(200, 100, 50))
        bean.SetNetImgRGB(test_image)
        retrieved = bean.GetNetImgRGB()
        # 修改返回的图像
        pixels = retrieved.load()
        pixels[0, 0] = (0, 0, 0)
        # 验证内部图像未被修改
        internal_pixels = bean.NetImgRGB.load()
        assert internal_pixels[0, 0] == (200, 100, 50)

    def test_get_net_img_rgb_when_none(self):
        """测试当未设置时返回None"""
        bean = ImgBean()
        result = bean.GetNetImgRGB()
        assert result is None


class TestSetPicList:
    """测试 SetPicList 方法"""

    def test_set_pic_list_with_valid_list(self):
        """测试使用有效的列表设置图片列表"""
        bean = ImgBean()
        test_list = ['image1.jpg', 'image2.jpg', 'image3.jpg']
        result = bean.SetPicList(test_list)
        assert result is True
        assert bean.PicList == test_list
        assert len(bean.PicList) == 3

    def test_set_pic_list_copies_list(self):
        """测试深拷贝：修改原始列表不影响内部存储"""
        bean = ImgBean()
        test_list = ['a.jpg', 'b.jpg']
        bean.SetPicList(test_list)
        # 修改原始列表
        test_list.append('c.jpg')
        # 验证内部列表未被修改
        assert len(bean.PicList) == 2

    def test_set_pic_list_with_empty_list(self):
        """测试空列表"""
        bean = ImgBean()
        test_list = []
        result = bean.SetPicList(test_list)
        assert result is True
        assert bean.PicList == []

    def test_set_pic_list_with_nested_list(self):
        """测试嵌套列表"""
        bean = ImgBean()
        test_list = [['a1.jpg', 'a2.jpg'], ['b1.jpg']]
        result = bean.SetPicList(test_list)
        assert result is True
        assert bean.PicList == test_list

    def test_set_pic_list_with_dict_list(self):
        """测试包含字典的列表"""
        bean = ImgBean()
        test_list = [{'path': 'img.jpg', 'id': 1}, {'path': 'img2.jpg', 'id': 2}]
        result = bean.SetPicList(test_list)
        assert result is True
        assert bean.PicList == test_list

    def test_set_pic_list_modify_inner_element_does_not_affect_original(self):
        """测试修改内部元素不影响原始列表"""
        bean = ImgBean()
        test_list = [{'path': 'img.jpg', 'id': 1}]
        bean.SetPicList(test_list)
        # 修改原始列表的内部字典
        test_list[0]['id'] = 999
        # 验证内部字典未被修改
        assert bean.PicList[0]['id'] == 1

    def test_set_pic_list_with_non_list_input_returns_false(self):
        """测试非列表输入返回False"""
        bean = ImgBean()
        # 测试字符串
        result = bean.SetPicList("not a list")
        assert result is False
        assert bean.PicList == []

    def test_set_pic_list_with_dict_input_returns_false(self):
        """测试字典输入返回False"""
        bean = ImgBean()
        result = bean.SetPicList({'key': 'value'})
        assert result is False
        assert bean.PicList == []

    def test_set_pic_list_with_tuple_input_returns_false(self):
        """测试元组输入返回False"""
        bean = ImgBean()
        result = bean.SetPicList(('item1', 'item2'))
        assert result is False
        assert bean.PicList == []

    def test_set_pic_list_with_none_input_returns_false(self):
        """测试None输入返回False"""
        bean = ImgBean()
        result = bean.SetPicList(None)
        assert result is False
        assert bean.PicList == []

    def test_set_pic_list_with_integer_input_returns_false(self):
        """测试整数输入返回False"""
        bean = ImgBean()
        result = bean.SetPicList(123)
        assert result is False
        assert bean.PicList == []


class TestGetPicList:
    """测试 GetPicList 方法"""

    def test_get_pic_list_returns_copy(self):
        """测试返回的是深拷贝而非引用"""
        bean = ImgBean()
        test_list = ['img1.jpg', 'img2.jpg']
        bean.SetPicList(test_list)
        retrieved = bean.GetPicList()
        # 修改返回的列表
        retrieved.append('img3.jpg')
        # 验证内部列表未被修改
        assert len(bean.PicList) == 2

    def test_get_pic_list_modify_inner_does_not_affect_original(self):
        """测试修改返回列表的内部元素不影响原始数据"""
        bean = ImgBean()
        test_list = [{'name': 'test'}]
        bean.SetPicList(test_list)
        retrieved = bean.GetPicList()
        retrieved[0]['name'] = 'modified'
        # 验证内部数据未被修改
        assert bean.PicList[0]['name'] == 'test'

    def test_get_pic_list_when_empty(self):
        """测试当列表为空时返回空列表的深拷贝"""
        bean = ImgBean()
        result = bean.GetPicList()
        assert result == []
        # 验证返回的是拷贝而非同一个对象
        result.append('item')
        assert bean.PicList == []


class TestImgBeanIntegration:
    """测试 ImgBean 类的集成场景"""

    def test_full_workflow(self):
        """测试完整的工作流程"""
        bean = ImgBean()

        # 1. 设置和获取摄像头帧
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        assert bean.SetCamFrameRGB(frame) is True
        retrieved_frame = bean.GetCamFrameRGB()
        assert np.array_equal(retrieved_frame, frame)

        # 2. 设置和获取Qt图像
        qt_image = Image.new('RGB', (800, 600), color=(255, 0, 0))
        assert bean.SetQtImgRGB(qt_image) is True
        retrieved_qt = bean.GetQtImgRGB()
        assert retrieved_qt.size == (800, 600)

        # 3. 设置和获取网络图像
        net_image = Image.new('RGB', (640, 480), color=(0, 255, 0))
        assert bean.SetNetImgRGB(net_image) is True
        retrieved_net = bean.GetNetImgRGB()
        assert retrieved_net.size == (640, 480)

        # 4. 设置和获取图片列表
        pic_list = ['img1.jpg', 'img2.jpg', 'img3.jpg']
        assert bean.SetPicList(pic_list) is True
        retrieved_list = bean.GetPicList()
        assert retrieved_list == pic_list

    def test_multiple_set_operations(self):
        """测试多次设置操作会覆盖之前的数据"""
        bean = ImgBean()

        # 第一次设置
        frame1 = np.zeros((10, 10, 3), dtype=np.uint8)
        bean.SetCamFrameRGB(frame1)

        # 第二次设置
        frame2 = np.ones((20, 20, 3), dtype=np.uint8) * 255
        bean.SetCamFrameRGB(frame2)

        # 验证数据已被覆盖
        assert bean.CameraFrameRGB.shape == (20, 20, 3)
        assert np.all(bean.CameraFrameRGB == 255)

    def test_set_invalid_type_for_cam_frame(self):
        """测试设置无效类型到CamFrameRGB"""
        bean = ImgBean()
        # 尝试使用非numpy数组
        result = bean.SetCamFrameRGB([[1, 2, 3], [4, 5, 6]])
        # 这个会触发AttributeError因为列表没有copy方法
        # 但由于使用了try-except或方法内部处理，测试需要验证行为
        # 注意：根据当前实现，如果传入列表，Frame.copy()会失败
        # 这里假设方法应该处理这种情况或让异常抛出
        with pytest.raises(AttributeError):
            bean.SetCamFrameRGB([1, 2, 3])


class TestCurrLocalPicNum:
    """测试 CurrLocalPicNum 属性"""

    def test_initial_value(self):
        """测试初始值为0"""
        bean = ImgBean()
        assert bean.CurrLocalPicNum == 0

    def test_can_be_modified_directly(self):
        """测试可以直接修改该属性"""
        bean = ImgBean()
        bean.CurrLocalPicNum = 10
        assert bean.CurrLocalPicNum == 10
