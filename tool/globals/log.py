import sys
from datetime import datetime
import os

class PrintRedirect:
    def __init__(self, logfilepath):
        self.terminal = sys.stdout
        self.log = open(logfilepath, "a")

    def write(self, message):
        if self.terminal:
            self.terminal.write(message)
        if self.log:
            self.log.write(message)
        self.flush()

    def flush(self):
        if self.terminal:
            self.terminal.flush()
        if self.log:
            self.log.flush()

class log():
    def __init__(self, audiocleanlog = True, logmax = 10):
        self.logfilepath = ''
        self.audioclean = audiocleanlog
        self.logmax = logmax   

    def get_executable_directory(self):
        if getattr(sys, 'frozen', False):
            # 应用程序是打包后的可执行文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 应用程序是在解释器中运行的
            application_path = os.path.dirname(os.path.abspath(__file__))
        return application_path

    def get_log_path(self):
        base_path = self.get_executable_directory()
        return os.path.join(base_path, 'log')
    
    # 获取可执行文件同级目录下的文件路径
    def get_logfile_path(self, filename):
        base_path = self.get_log_path()
        return os.path.join(base_path, filename)

    def LogRun(self):
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"log_{timestamp}.log"
        print("log file name",filename)
        filepath = self.get_logfile_path(filename)
        print("log file path", filepath)
        # 清空缓存
        if self.audioclean:
            logpath = self.get_log_path()
            log_files = sorted([f for f in os.listdir(logpath) if f.startswith("log_") and f.endswith(".log")])
            print("文件个数",len(log_files))
            print("文件", log_files)
            # 如果日志文件个数超过10个，则删除最旧的文件，保留后10个
            if len(log_files) > self.logmax:
                for old_log in log_files[:-self.logmax]:
                    os.remove(os.path.join(logpath, old_log))
                    print(f"删除旧日志文件：{old_log}")
        # 重定向标准输出到文件
        sys.stdout = PrintRedirect(filepath)
        sys.stderr = sys.stdout  # 将标准错误输出重定向到同一文件
        print("发送端上位机开始运行. ",timestamp)
        print("")
        print("")


    def LogEnd(self):
        # 恢复标准输出到控制台
        sys.stdout = sys.__stdout__

# if __name__ == "__main__":
#     mylog = log()
#     mylog.LogRun()
#     # timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
#     # log_file_name = f"log_{timestamp}.log"
#     # # 重定向标准输出到文件
#     # sys.stdout = PrintRedirect(log_file_name)

#     # # 示例：打印一些输出
#     print("This will be logged to the file.")
#     print("Another line to log.")
#     mylog.LogEnd()
#     # # 恢复标准输出到控制台
#     # sys.stdout = sys.__stdout__

#     print("This will be printed on the console.")
