import queue


class QueueTool:

    @staticmethod
    def PutMsgQueue(q:queue.Queue, msg = None)->bool:
        """
        将消息放入队列
        Args:
            q: 目标队列
            msg: 要放入队列的消息，默认为None
        Returns:
            bool: 成功放入返回True，否则返回False
        """
        if not q.full():  # 检查队列是否满
            try:
                q.put(msg, block=False)  # 尝试放入队列
                return True
            except queue.Full:
                print("PutMsgQueue failed: Queue is full")
                return False
        else:
            return False

    @staticmethod
    def GetMsgQueue(q: queue.Queue):
        """非阻塞获取消息，无消息返回None"""
        if q.empty():
            return None
        try:
            return q.get(block=False)
        except queue.Empty:
            return None
        
    @staticmethod
    def GetMsgQueueBlock(q: queue.Queue, timeout=None):
        """
        阻塞读取队列（线程专用，不占CPU）
        :param q: 队列
        :param timeout: 超时时间（秒），默认一直等
        :return: 消息 / None（超时/空）
        """
        try:
            return q.get(block=True, timeout=timeout)
        except queue.Empty:
            return None
        
    @staticmethod
    def ClearMsgQueue(q: queue.Queue) -> None:
        """
        清空指定队列中的所有消息
        Args:
            q: 要清空的目标队列
        Returns:
            None
        """
        if q is None:
            return
        try:
            while not q.empty():
                q.get(block=False)  # 非阻塞取出所有数据
        except queue.Empty:
            pass
        except Exception as e:
            print(f"ClearMsgQueue failed: {str(e)}")



