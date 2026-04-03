import threading
import queue
import random
import time

TS_FILE = ".\\images\\1.ts"
OUTPUT_FILE = ".\\images\\recovered.ts"
CHUNK_SIZE = 1316      # 每块大小
LOSS_RATE = 0.1        # 模拟丢包概率
MAX_DELAY = 0.001       # 模拟网络乱序最大延迟（秒）

# 模拟“网络队列”
network_queue = queue.Queue()

# 全局变量记录总包数
total_packets = 0

def sender():
    """线程 A：读取 TS 文件，打包发送"""
    global total_packets
    print("发送线程启动，开始读取 TS 文件...")
    with open(TS_FILE, "rb") as f:
        seq = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            packet = (seq, chunk)
            seq += 1
            total_packets += 1
            # 模拟丢包
            if random.random() > LOSS_RATE:
                # 模拟乱序延迟
                time.sleep(random.uniform(0, MAX_DELAY))
                network_queue.put(packet)
    # 发送结束信号
    network_queue.put(None)
    print(f"发送完成，总包数：{total_packets}")

def receiver():
    """线程 B：接收 TS 块，可能乱序、丢包"""
    received = {}
    print("接收线程启动，等待数据...")
    while True:
        
        packet = network_queue.get()
        if packet is None:
            break
        seq, chunk = packet
        # 写入字典，可能乱序
        received[seq] = chunk

    # 按序号写出 TS 文件（丢失的包跳过）
    with open(OUTPUT_FILE, "wb") as f:
        for seq in sorted(received.keys()):
            f.write(received[seq])

    lost_count = total_packets - len(received)
    print(f"接收完成，TS 文件已还原（可能缺帧）")
    print(f"总包数：{total_packets}，接收包数：{len(received)}，丢失包数：{lost_count}")

# 启动线程
t1 = threading.Thread(target=sender)
t2 = threading.Thread(target=receiver)
t1.start()
t2.start()
t1.join()
t2.join()