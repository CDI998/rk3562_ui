import cv2
from cv2 import dnn_superres

# 创建对象
sr = dnn_superres.DnnSuperResImpl_create()

# 加载 pb 模型
sr.readModel("ESPCN_x3.pb")

# 设置模型
sr.setModel("espcn", 3)

# 读取图片
img = cv2.imread(r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\photo.jpg")

# 超分辨率
result = sr.upsample(img)

# 保存
cv2.imwrite(r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\output.jpg", result)