from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from threading import Thread
import cv2
from socket import *
import numpy
# 主机地址为空字符串，表示绑定本机所有网络接口ip地址
IP = ''
# 端口号
PORT = 50001
# 定义一次从socket缓冲区最多读入60000个字节数据
BUFLEN = 60000
Send_BUFLEN = 1024
class Server():
    def __init__(self):
        # data=Data()
        self.ui = uic.loadUi('./server_latest.ui')
        self.ui.establish.clicked.connect(self.Establish)
        self.ui.shut.clicked.connect(self.Shut)
        self.ui.open_videoTCP.clicked.connect(self.Video_TCP)
        self.ui.open_videoUDP.clicked.connect(self.Video_UDP)
        self.ui.shut_video.clicked.connect(self.Shut_Video)
        self.ui.open_chat.clicked.connect(self.Chat)
        self.ui.send.clicked.connect(self.Server_Send)
        self.dataSocket = None
        self.serverSocket = None
        self.TCPsocket = None
        self.UDPsocket = None
        self.addr = []
        self.address_all = []
        self.count = 0



    def Establish(self):
        self.count = 0
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
        th = Thread(target=self.start, args=())
        # 设置新线程为daemon线程
        th.setDaemon(True)
        # 执行start 方法，就会创建新线程，
        # 并且新线程会去执行入口函数里面的代码。
        # 这时候 这个进程 有两个线程了
        th.start()

    def start(self):
        # 此处采用阻塞式监听
        print('等待客户端的连接...')
        self.dataSocket, addr = self.serverSocket.accept()
        self.count = self.count + 1
        print('接受一个客户端连接:', addr,'  目前在线人数为：',self.count)
        self.dataSocket.send('已连接到服务端，可以发送消息啦！'.encode())
        th = Thread(target=self.recv,args=(self.dataSocket,))
        th.setDaemon(True)
        th.start()

    def recv(self,dataSocket):
        while True:
            # 尝试读取对方发送的消息
            # BUFLEN 指定从接收缓冲里最多读取多少字节
            recved = dataSocket.recv(Send_BUFLEN)
            # 如果返回空bytes，表示对方关闭了连接
            # 退出循环，结束消息收发
            if not recved:
                break
            # 读取的字节数据是bytes类型，需要解码为字符串
            info = recved.decode()
            self.ui.out_message.appendPlainText(f'收到对方信息： {info}')
            # 发送的数据类型必须是bytes，所以要编码
            dataSocket.send(f'服务端接收到了信息: {info}'.encode())
        dataSocket.close()


    def Shut(self):
        # 服务端也调用close()关闭socket
        self.serverSocket.close()

    def Chat(self):
        self.count = 0
        # 实例化一个socket对象
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        # socket绑定地址和端口
        self.serverSocket.bind((IP, PORT))
        # 使socket处于监听状态，等待客户端的连接请求
        self.serverSocket.listen(8)
        th = Thread(target=self.Chat_start, args=())
        # 设置新线程为daemon线程
        th.setDaemon(True)
        th.start()

    def Chat_start(self):
        # 此处采用阻塞式监听
        while True:
            self.ui.out_message.appendPlainText('等待其他用户的连接...')
            dataSocket, address = self.serverSocket.accept()
            self.count = self.count + 1
            self.addr.append(dataSocket)
            self.address_all.append(address[0])
            print('接受一个用户连接:', address,'  目前在线人数为：',self.count)
            dataSocket.send('已连接到群聊天，可以发送消息啦！'.encode())
            th = Thread(target=self.Chat_recv,args=(dataSocket,))
            th.setDaemon(True)
            th.start()

    def Chat_recv(self,dataSocket):
        while True:
            # 尝试读取对方发送的消息
            # BUFLEN 指定从接收缓冲里最多读取多少字节
            recved = dataSocket.recv(Send_BUFLEN)
            # 如果返回空bytes，表示对方关闭了连接
            # 退出循环，结束消息收发
            if not recved:
                break
            # 读取的字节数据是bytes类型，需要解码为字符串
            info = recved.decode()
            count_temp = 0
            for iii in self.addr:
                if iii == dataSocket:
                    break
                count_temp = count_temp + 1
            # print(self.address_all[count_temp])
            temp_str = str(self.address_all[count_temp])+f'的信息：{info}'
            self.ui.out_message.appendPlainText(temp_str)
            # 发送的数据类型必须是bytes，所以要编码
            for ii in self.addr:
                if ii != dataSocket:
                    ii.send(temp_str.encode())
        dataSocket.close()

    def Server_Send(self):
        # 接受框中的消息
        toSend = self.ui.in_message.toPlainText()
        # 接收完成后，清空消息
        self.ui.in_message.clear()
        # 发送消息，也要编码为 bytes
        for ii in self.addr:
            s = f'客户端的信息：{toSend}'
            ii.send(s.encode())
        ss = '我：'+toSend
        self.ui.out_message.appendPlainText(ss)
        return

    def Video_TCP(self):
        self.ui.out_message.appendPlainText('Server: Ready for the Transmission of video')
        self.TCPsocket = socket(AF_INET, SOCK_STREAM)
        self.ui.out_message.appendPlainText('Server: Choose the TCP protocol')
        # 将Socket（套接字）绑定到地址
        self.TCPsocket.bind((IP, PORT))
        self.ui.out_message.appendPlainText('Server: Binding the IP and PORT')
        # 最多监听8个端口
        self.TCPsocket.listen(8)
        self.ui.out_message.appendPlainText('Server: Waiting for connecting videos using TCP...')
        # 接受TCP连接并返回，其中conn是新的套接字对象，可以用来接收和发送数据，addr是链接客户端的地址。
        th = Thread(target=self.Video_accept_TCP, args=())
        th.setDaemon(True)
        th.start()

    def Video_accept_TCP(self):
        conn, addr = self.TCPsocket.accept()
        self.ui.out_message.appendPlainText('Successfully connected using TCP protocol ')
        th = Thread(target=self.Video_star_TCP, args=(conn,))
        th.setDaemon(True)
        th.start()


    def Video_star_TCP(self,connect):
        while True:
            # 循环接收每一帧数据
            length = connect.recv(1024).decode()
            print('客户端发送的大小信息:',length)  # 首先接收来自客户端发送的大小信息
            if length == "Close":
                break
            if length != 0:
                # 确认已经接受数据长度
                connect.send('ACK'.encode())
                # 接收整张图片
                bytedata = connect.recv(BUFLEN)
                img = numpy.asarray(bytearray(bytedata), dtype="uint8")
                # 解码进行显示
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                cv2.imshow("server_TCP", img)
                connect.send('ACK'.encode())
                if cv2.waitKey(1) == 27:
                    self.Shut_Video()
                    break

    def Shut_Video(self):
        if self.TCPsocket != None:
            self.ui.out_message.appendPlainText('TCP已断开连接')
            self.TCPsocket.close()
        if self.UDPsocket != None:
            self.ui.out_message.appendPlainText('UDP已断开连接')
            self.UDPsocket.close()
        cv2.destroyAllWindows()

    def Video_UDP(self):
        self.ui.out_message.appendPlainText('Server: Ready for the Transmission of video')
        self.UDPsocket = socket(AF_INET,SOCK_DGRAM)
        self.ui.out_message.appendPlainText('Server: Choose the UDP protocol')
        # 将Socket（套接字）绑定到地址
        self.UDPsocket.bind((IP, PORT))
        self.ui.out_message.appendPlainText('Server: Binding the IP and PORT')
        th = Thread(target=self.Video_star_UDP, args=())
        th.setDaemon(True)
        th.start()

    # def Video_listen_UDP(self):
    #     # 最多监听8个端口
    #     self.ui.out_message.appendPlainText('Waiting for connecting videos using UDP...')
    #     th = Thread(target=self.Video_star_UDP, args=())
    #     th.setDaemon(True)
    #     th.start()

    def Video_star_UDP(self):
        self.ui.out_message.appendPlainText('Waiting for the videos message using UDP...')
        # 循环接收每一帧数据
        while True:
            length, addr = self.UDPsocket.recvfrom(1024)  # 首先接收来自客户端发送的大小信息
            length = length.decode()

            # 数据包小于60000，可以直接发送
            if int(length) != 0:
                # 确认数据长度,回复ack
                self.UDPsocket.sendto('ACK'.encode(), addr)
                # 接收整张图片
                bytedata, self.addr = self.UDPsocket.recvfrom(BUFLEN)
                # 接收完一帧数据
                self.UDPsocket.sendto('ACK'.encode(), addr)
                data = numpy.asarray(bytearray(bytedata), dtype="uint8")
                # 解码进行显示
                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                cv2.imshow("server_UDP", img)
                if cv2.waitKey(1) == 27:
                    self.Shut_Video()
                    break


app = QApplication([])
stats = Server()
stats.ui.show()
app.exec_()