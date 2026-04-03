import sys
import cv2
import time
import threading
import queue
import subprocess
import numpy as np

# 队列存储摄像头帧
frame_queue = queue.Queue(maxsize=20)
FRAME_COUNT_TO_SAVE = 10
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
OUTPUT_VIDEO = "output.mp4"

def camera_thread():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    print("Camera thread started.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not frame_queue.full():
            frame_queue.put(rgb_frame)
        else:
            print("Frame queue is full, dropping frame.")
        time.sleep(0.1)
        # for _ in range(2):
        #     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     if not frame_queue.full():
        #         frame_queue.put(rgb_frame)
        #     time.sleep(0.1)

    cap.release()

def generate_video_from_queue():
    """
    从队列获取 FRAME_COUNT_TO_SAVE 帧，通过 FFmpeg 管道生成 MP4 并插帧到 30fps
    """
    # 等待队列里至少有 FRAME_COUNT_TO_SAVE 帧
    while frame_queue.qsize() < FRAME_COUNT_TO_SAVE:
        time.sleep(0.1)

    frames = []
    for _ in range(FRAME_COUNT_TO_SAVE):
        frame = frame_queue.get()
        frames.append(frame)

    # FFmpeg 命令
    # ffmpeg_cmd = [
    #     "ffmpeg",
    #     "-y",  # 覆盖输出文件
    #     "-f", "rawvideo",
    #     "-pix_fmt", "rgb24",
    #     "-s", f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
    #     "-r", "2",  # 输入帧率
    #     "-i", "pipe:0",
    #     "-vf", "minterpolate=fps=30",
    #     "-pix_fmt", "yuv420p",
    #     OUTPUT_VIDEO
    # ]

    ffmpeg_cmd = [
    "ffmpeg",
    "-y",
    "-f", "rawvideo",
    "-pix_fmt", "rgb24",
    "-s", f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
    "-r", "10",  # 输入帧率
    "-i", "pipe:0",
    "-vf", "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    OUTPUT_VIDEO
    ]

    print(f"Writing {FRAME_COUNT_TO_SAVE} frames to FFmpeg...")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    for f in frames:
        proc.stdin.write(f.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"Video generated: {OUTPUT_VIDEO}")

def main():
    # 启动摄像头线程
    t1 = threading.Thread(target=camera_thread, daemon=True)
    t1.start()

    # 等待队列满并生成视频
    generate_video_from_queue()

if __name__ == "__main__":
    main()