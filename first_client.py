from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from socket import *
IP = '127.0.0.1'  # 10.5.228.94  127.0.0.1
SERVER_PORT = 50001
BUFLEN = 1024

class Client():
    def __init__(self):
        self.ui = uic.loadUi('./first_client.ui')
        self.ui.establish.clicked.connect(self.getConnect)
        self.ui.send.clicked.connect(self.Send)
        self.ui.shut.clicked.connect(self.Shut)
        self.dataSocket = None

    def getConnect(self):

        # 实例化一个socket对象，指明协议
        self.dataSocket = socket(AF_INET, SOCK_STREAM)
        # 连接服务端socket
        self.dataSocket.connect((IP, SERVER_PORT))
    def Send(self):
        # 接受框中的消息
        toSend = self.ui.in_message.toPlainText()
        # 接收完成后，清空消息
        self.ui.in_message.clear()
        # 发送消息，也要编码为 bytes
        self.dataSocket.send(toSend.encode())
        # 等待接收服务端的消息
        recved = self.dataSocket.recv(BUFLEN)
        # 如果返回空bytes，表示对方关闭了连接
        if not recved:
            return
        self.ui.out_message.appendPlainText(recved.decode())

    def Shut(self):
        self.dataSocket.close()
app = QApplication([])
stats = Client()
stats.ui.show()
app.exec_()
