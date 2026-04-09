import cv2
import os
import numpy as np

# ==============================
# 1. 图片切块函数（你要求的格式）
# ==============================
def split_jpeg_to_blocks(image_path: str, x_blocks: int, y_blocks: int):
    x_blocks = max(1, min(x_blocks, 10))
    y_blocks = max(1, min(y_blocks, 10))
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    block_w = w // x_blocks
    block_h = h // y_blocks
    result = []

    for y in range(y_blocks):
        row_start_id = y * 10
        for x in range(x_blocks):
            current_id = row_start_id + x
            x1 = x * block_w
            y1 = y * block_h
            x2 = x1 + block_w
            y2 = y1 + block_h
            block = img[y1:y2, x1:x2]
            _, encoded = cv2.imencode(".jpg", block)
            result.append({"id": current_id, "data": encoded.tobytes()})
    return result


# ==============================
# 2. 块贴回图片函数（你要的新函数）
# ==============================
def paste_block_to_image(
    target_img: np.ndarray,
    block: dict,
    total_x_blocks: int,
    total_y_blocks: int
):
    """
    把一个块（id+data）贴到目标图片的正确位置
    :param target_img: 目标图片（空白/原图）
    :param block: {"id": 编号, "data": 二进制}
    :param total_x_blocks: 总列数（切块时的x）
    :param total_y_blocks: 总行数（切块时的y）
    :return: 贴好的图片
    """
    block_id = block["id"]
    data = block["data"]

    # 解码图片块
    block_data = np.frombuffer(data, dtype=np.uint8)
    block_img = cv2.imdecode(block_data, cv2.IMREAD_COLOR)

    h, w = target_img.shape[:2]
    block_w = w // total_x_blocks
    block_h = h // total_y_blocks

    # 计算坐标
    y = block_id // 10        # 行 = 0,1,2,3,4...
    x = block_id % 10         # 列 = 0~9
    x1 = x * block_w
    y1 = y * block_h

    # 把块贴到目标图上
    target_img[y1:y1+block_h, x1:x1+block_w] = block_img

    return target_img


# ==============================
# 3. 测试函数（完整流程）
# ==============================
def test_merge_blocks():
    # 路径
    img_path = r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\photo.jpg"
    save_dir = r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\testdata"
    os.makedirs(save_dir, exist_ok=True)

    # 配置
    X = 5
    Y = 5

    # 1. 切块
    blocks = split_jpeg_to_blocks(img_path, x_blocks=X, y_blocks=Y)

    # 2. 读取原图获取尺寸，创建空白图
    src = cv2.imread(img_path)
    h, w = src.shape[:2]
    blank_img = np.zeros((h, w, 3), dtype=np.uint8)  # 黑色空白图

    # 3. 挑选两个块 【你可以随便改】
    block1 = next(b for b in blocks if b["id"] == 0)
    block2 = next(b for b in blocks if b["id"] == 11)

    # 4. 贴上去
    blank_img = paste_block_to_image(blank_img, block1, X, Y)
    blank_img = paste_block_to_image(blank_img, block2, X, Y)

    # 5. 保存结果
    out_path = os.path.join(save_dir, "merged_result.jpg")
    cv2.imwrite(out_path, blank_img)
    print("✅ 拼接完成，保存到：", out_path)


if __name__ == "__main__":
    test_merge_blocks()