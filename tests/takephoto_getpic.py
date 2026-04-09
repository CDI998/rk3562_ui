import cv2
import time
import os

# ===================== 配置 =====================
# 摄像头编号（一般 0 是默认摄像头）
CAMERA_INDEX = 0

# 拍照张数、间隔
CAPTURE_COUNT = 5
INTERVAL_SEC  = 3

# 保存路径（Win10 路径）
SAVE_DIR = r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tool\globals\data\local\pics"

# 图片尺寸
WIDTH = 640
HEIGHT = 480
# ================================================

# 自动创建目录
os.makedirs(SAVE_DIR, exist_ok=True)

# 打开摄像头
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if not cap.isOpened():
    print("摄像头打开失败！")
    input("按回车退出")
    exit()

print(f"✅ 摄像头已打开，将每 {INTERVAL_SEC} 秒拍一张，共 {CAPTURE_COUNT} 张")

for i in range(1, CAPTURE_COUNT + 1):
    print(f"\n等待 {INTERVAL_SEC} 秒后拍摄第 {i}/{CAPTURE_COUNT} 张...")
    time.sleep(INTERVAL_SEC)

    ret, frame = cap.read()
    if not ret:
        print(f"❌ 第 {i} 张拍摄失败")
        continue

    save_path = os.path.join(SAVE_DIR, f"photo_{i:02d}.jpg")
    cv2.imwrite(save_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"📸 已保存：{save_path}")

cap.release()
cv2.destroyAllWindows()

print("\n🎉 5张照片拍摄完成！")
input("按回车退出")