import cv2
import os

def split_jpeg_to_blocks(image_path: str, x_blocks: int, y_blocks: int):
    """
    将 JPEG 切割成 x*y 块，返回 编号+图片二进制数据
    行ID规则：第1行=0，第2行=10，第3行=20 ... 最大10行
    每行最多10块，最多10行
    返回：列表 [ {"id": 编号, "data": 图片编码数据}, ... ]
    """
    # 安全限制
    x_blocks = max(1, min(x_blocks, 10))
    y_blocks = max(1, min(y_blocks, 10))

    # 读取原图
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图片：{image_path}")

    h, w = img.shape[:2]
    block_w = w // x_blocks
    block_h = h // y_blocks

    result = []

    # 切割
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


# ------------------------------
# 测试代码（5×5 切割 + 按ID保存）
# ------------------------------
if __name__ == "__main__":
    # 输入图片路径
    input_img = r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\photo.jpg"
    # 输出目录
    output_dir = r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\testdata"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 切割 5列 × 5行
    blocks = split_jpeg_to_blocks(input_img, x_blocks=5, y_blocks=5)

    # 按编号保存
    for block in blocks:
        block_id = block["id"]
        data = block["data"]
        save_path = os.path.join(output_dir, f"{block_id}.jpeg")

        with open(save_path, "wb") as f:
            f.write(data)

    print(f"✅ 切割完成！共 {len(blocks)} 块，已保存到：{output_dir}")