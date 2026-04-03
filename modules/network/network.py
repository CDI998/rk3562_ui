import socket
from threading import Thread
from PyQt5.QtCore import pyqtSignal as Signal
import queue
# from data import databean
# import time

class NetWorkMode():
    def __init__(self, NetQueueTx:queue,  # 接收网络包时触发信号，传递数据和IP
                 NetQueueRx:queue,  # 发送网络包时间，往队列中写入数据
                 MyIp = "192.168.1.9",
                 BoardIp="192.168.1.1", 
                 DefUdpDestIp="255.255.255.255",
                 port=1234):
        Thread.__init__(self)
        self.NetQueueTx = NetQueueTx  # 线程队列
        self.NetQueueRx = NetQueueRx  # 线程队列
        self.BoardIp = BoardIp
        self.MyIp = MyIp
        self.DefUdpDestIp = DefUdpDestIp
        self.Port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        local_addr = (self.MyIp, self.Port)
        self.sock.bind(local_addr)
        self.Rx_running = True
        self.Tx_running = True

        self.recvthread = Thread(target=self.receive_net_message, args=())
        self.recvthread.daemon = True
        self.sendthread = Thread(target=self.send_net_message, args=())
        self.sendthread.daemon = True

    def send_udp_msg(self, message:bytes, addr=("255.255.255.255", 1234)):
        return self.sock.sendto(message, addr)
    
    def send_net_message(self):
        while self.Tx_running:
            try:
                NetMsg = self.NetQueueTx.get()  # 无限期阻塞，直到队列中有数据
                # print("send_net_message:", type(NetMsg),type(NetMsg[0]), type(NetMsg[1]) )
                # self.send_udp_msg(NetMsg[0], NetMsg[1]) # udp发送
                if NetMsg is None or NetMsg[0] is None or NetMsg[1] is None:
                    # print("send_net_message:Thread recv None or invalid param")
                    self.NetQueueTx.task_done()
                    continue
                # print("send_net_message:", len(NetMsg[0]))
                self.sock.sendto(NetMsg[0], NetMsg[1])
                self.NetQueueTx.task_done()  # 通知队列该任务已处理完成
            except socket.error as e:
                print("send_net_message Error:",e)

    def receive_net_message(self):
        while self.Rx_running:
            try:
                data, addr = self.sock.recvfrom(1700)
                # print("Received message from", addr)
                # print(self.BoardIp,self.Port)
                if(addr[0] == self.BoardIp and int(addr[1]) == self.Port):
                    # print(addr, "Received message:", len(data))
                    self.SendQueueMsg(self.NetQueueRx, (data, addr))  # 发射信号，传递数据和IP
            except socket.error as e:
                if e.errno == 10038:  # WSAENOTSOCK
                    print("套接字已关闭，停止接收！！！")
                    break
                else:
                    raise

    def SendQueueMsg(self, q:queue, udpmsg = None):
        # print("SendQueueMsg")
        if not q.full():  # 检查队列是否满
            try:
                q.put(udpmsg, block=False)  # 尝试放入队列
                # print("UdpSendMsg:Message put into queue")
            except queue.Full:
                print("UdpSendMsg failed:Net Queue is full")
        else:
            # print("UdpSendMsg:Net Queue is full")
            pass

    def NetRun(self):
        self.Rx_running = True
        self.Tx_running = True
        self.sendthread.start()
        self.recvthread.start()

    def NetStop(self):
        self.Rx_running = False
        self.Tx_running = False
        self.sock.close()

# NetWorkTool = NetWorkThread(None, "", 1234)
# NetWorkTool.start()
# datatool = databean()
# udpmsg = datatool.buildMlmePacket(1, "12", 2)
# num = NetWorkTool.send_udp_message(udpmsg, "255.255.255.255", 1234)
# print(num)
# time.sleep(5)
# NetWorkTool.stop()
