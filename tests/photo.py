import cv2

pipeline = (
    "v4l2src device=/dev/video11 ! "
    "video/x-raw,format=NV12,width=640,height=320,framerate=30/1 ! "
    "videoconvert ! "
    "appsink"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

ret, frame = cap.read()

if ret:
    cv2.imwrite("test.jpg", frame)
    print("拍照成功")
else:
    print("拍照失败")

cap.release()