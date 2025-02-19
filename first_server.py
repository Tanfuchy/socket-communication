from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from socket import *
from threading import Thread

# 主机地址为空字符串，表示绑定本机所有网络接口ip地址
IP = ''
# 端口号
PORT = 50001
# 定义一次从socket缓冲区最多读入1024个字节数据
BUFLEN = 1024

class Server():
    def __init__(self):
        # data=Data()
        self.ui = uic.loadUi('./first_server.ui')
        self.ui.open.clicked.connect(self.Establish)
        self.ui.shut_2.clicked.connect(self.Shut_2)
        self.dataSocket = None
        self.serverSocket = None
        count = 0

    def recv(self,dataSocket):
        while True:
            # 尝试读取对方发送的消息
            # BU FLEN 指定从接收缓冲里最多读取多少字节
            recved = dataSocket.recv(BUFLEN)
            # 如果返回空bytes，表示对方关闭了连接
            # 退出循环，结束消息收发
            if not recved:
                break
            # 读取的字节数据是bytes类型，需要解码为字符串
            info = recved.decode()
            self.ui.out_message.appendPlainText(f'收到对方信息： {info}')
            # 发送的数据类型必须是bytes，所以要编码
            dataSocket.send(f'服务端接收到了信息 {info}'.encode())
        dataSocket.close()

    def start(self,count):
        # 此处采用阻塞式监听
        print('等待客户端的连接...')
        sock, addr = self.serverSocket.accept()
        count = count + 1
        print('接受一个客户端连接:', addr,'  目前在线人数为：',count)
        th = Thread(target=self.recv,args=(sock,))
        th.setDaemon(True)
        th.start()


    def Establish(self,count):
        # 实例化一个socket对象
        # 参数 AF_INET 表示该socket网络层使用IP协议
        # 参数 SOCK_STREAM 表示该socket传输层使用tcp协议
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        # socket绑定地址和端口
        self.serverSocket.bind((IP, PORT))
        # 使socket处于监听状态，等待客户端的连接请求
        # 最多接受8个等待连接的客户端
        self.serverSocket.listen(8)
        # target 参数 指定 新线程要执行的函数
        # 注意，这里指定的函数对象只能写一个名字，不能后面加括号，
        # 如果加括号就是直接在当前线程调用执行，而不是在新线程中执行了
        # 如果 新线程函数需要参数，在 args里面填入参数
        # 注意参数是元组， 如果只有一个参数，后面要有逗号，像这样 args=('参数1',)
        th = Thread(target=self.start, args=(count,))
        # 设置新线程为daemon线程
        th.setDaemon(True)
        # 执行start 方法，就会创建新线程，
        # 并且新线程会去执行入口函数里面的代码。
        # 这时候 这个进程 有两个线程了
        th.start()

    def Shut_2(self):
        # 服务端也调用close()关闭socket

        self.serverSocket.close()

app = QApplication([])
stats = Server()
stats.ui.show()
app.exec_()