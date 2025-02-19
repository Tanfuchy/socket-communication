#!/usr/bin/python
# -*-coding:utf-8 -*-
import cv2
import numpy
import time
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from socket import *
from threading import Thread
IP = '127.0.0.1'  # 10.5.228.94  127.0.0.1 192.168.43.97
SERVER_PORT = 50001
BUFLEN = 1024


class Client():
    def __init__(self):
        self.ui = uic.loadUi('./client_latest.ui')
        self.ui.establish.clicked.connect(self.getConnect)
        self.ui.send.clicked.connect(self.Send)
        self.ui.shut.clicked.connect(self.Shut)
        self.ui.open_videoTCP.clicked.connect(self.Video_TCP)
        self.ui.open_videoUDP.clicked.connect(self.Video_UDP)
        self.ui.shut_video.clicked.connect(self.Shut_Video)
        self.ui.open_chat.clicked.connect(self.Chat_Connect)
        self.toSend = None
        self.dataSocket = None
        self.TCPsocket = None
        self.UDPsocket = None
        self.address_server = None
        self.speed_count = 0
        self.choose = 0


    def getConnect(self):
        self.choose = 1
        # 实例化一个socket对象，指明协议
        self.dataSocket = socket(AF_INET, SOCK_STREAM)
        # 连接服务端socket
        self.dataSocket.connect((IP, SERVER_PORT))
        print('已连接上服务器 ip:', IP)
        recved = self.dataSocket.recv(BUFLEN)
        self.ui.out_message.appendPlainText(recved.decode())


    def Send(self):
        if self.choose == 1:
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
        elif self.choose == 2:
            # 接受框中的消息
            toSend = self.ui.in_message.toPlainText()
            # 接收完成后，清空消息
            self.ui.in_message.clear()
            # 发送消息，也要编码为 bytes
            self.dataSocket.send(toSend.encode())
            s = '我：'+toSend
            self.ui.out_message.appendPlainText(s)
        else:
            print('发送失败！')
            self.ui.out_message.appendPlainText('发送失败！')

    def Shut(self):
        self.dataSocket.close()
        self.choose = 0

    def Chat_Connect(self):
        self.choose = 2
        # 实例化一个socket对象，指明协议
        self.dataSocket = socket(AF_INET, SOCK_STREAM)
        # 连接服务端socket
        self.dataSocket.connect((IP, SERVER_PORT))
        # self.ui.out_message.appendPlainText('正在连接上群聊服务器 ip:', IP)
        print('正在连接上群聊服务器 ip:', IP)
        # 接收连接成功的消息
        recved = self.dataSocket.recv(BUFLEN)
        self.ui.out_message.appendPlainText(recved.decode())
        th = Thread(target=self.Chat_start, args=())
        # 设置新线程为daemon线程
        th.setDaemon(True)
        th.start()

    def Chat_start(self):
        while True:
            # 尝试读取对方发送的消息
            # BUFLEN 指定从接收缓冲里最多读取多少字节
            recved = self.dataSocket.recv(BUFLEN)
            # 如果返回空bytes，表示对方关闭了连接
            # 退出循环，结束消息收发
            if not recved:
                break
            # 读取的字节数据是bytes类型，需要解码为字符串
            info = recved.decode()
            self.ui.out_message.appendPlainText(info)
            # 发送的数据类型必须是bytes，所以要编码
        self.dataSocket.close()

    def Video_TCP(self):
        # socket.AF_INET 用于服务器与服务器之间的网络通信
        # socket.SOCK_STREAM 代表基于TCP的流式socket通信
        self.ui.out_message.appendPlainText('Client: Ready for the Transmission of video')
        self.TCPsock = socket(AF_INET,SOCK_STREAM)
        self.ui.out_message.appendPlainText('Client: Choose the TCP protocol')
        # 连接服务端
        address_server = (IP, SERVER_PORT)
        self.ui.out_message.appendPlainText('Client: Binding the IP and PORT')
        self.ui.out_message.appendPlainText('Client: Waiting for connecting videos using TCP...')
        self.TCPsock.connect(address_server)
        self.ui.out_message.appendPlainText('Client: Successfully connecting videos using TCP!')
        # 从摄像头采集图像
        # 参数是0,表示打开笔记本的内置摄像头,参数是视频文件路径则打开视频
        capture = cv2.VideoCapture(0)
        # capture.read() 按帧读取视频
        # ret,frame 是capture.read()方法的返回值
        # 其中ret是布尔值，如果读取帧正确，返回True;如果文件读到末尾，返回False。
        # frame 就是每一帧图像，是个三维矩阵
        ret, frame = capture.read()
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
        self.ui.out_message.appendPlainText('Goto show the video')
        th = Thread(target=self.TCP_start, args=(ret,frame,encode_param,capture))
        th.setDaemon(True)
        th.start()

    def TCP_start(self,ret,frame,encode_param,capture):
        while ret:
            # 首先对图片进行编码，因为socket不支持直接发送图片
            # '.jpg'表示把当前图片frame按照jpg格式编码
            # result, img_encode = cv2.imencode('.jpg', frame)
            # 压缩图像
            img_encode = cv2.imencode('.jpg', frame, encode_param)[1]
            # 转换为字节流
            bytedata = img_encode.tobytes()
            # 将输入数据转换为矩阵形式
            # bytearray返回一个新字节数组 读取了图片并显示出来，那么存储的数据格式必须为uint8
            data = numpy.asarray(bytearray(bytedata), dtype="uint8")
            # 解码进行显示
            # bool imencode(const String& ext, InputArray img, vector<uchar>& buf, const vector<int>& params=vector<int>())
            # ext-定义输出文件格式的扩展名 img-需要被编码的图像 buf-输出的缓存区，类型是vector parms-被编码的格式和压缩率,类型是vector 默认使用该种标识。
            # cv2.IMREAD_COLOR加载一张彩色图片，忽视它的透明度。
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            # 载入的图片显示
            cv2.imshow("client_TCP", img)
            # cv2.waitKey(int delay)不断刷新图像，频率为delay，单位是ms，返回值为当前键盘按下的值，没有按键时返回-1.
            c = cv2.waitKey(1)
            stringData = data.tostring()
            # 生成标志数据
            # 首先发送图片编码后的长度
            self.TCPsock.send(str(len(stringData)).encode())

            ret, frame = capture.read()
            cv2.resize(frame, (640, 480))

            # 接收服务端的应答,准备计时
            data_re = self.TCPsock.recv(1024)
            if (data_re.decode() == 'ACK'):
                # 开始计时
                self.speed_count = self.speed_count + 1
                start = time.perf_counter()
                # 服务端已经收到标志数据，开始发送图像字节流数据
                self.TCPsock.send(bytedata)
                # 计算发送完成的延时
                data_re = self.TCPsock.recv(1024 * 1024)
                if data_re.decode() == "ACK":
                    end = time.perf_counter()
                    delay = (end - start) * 1000
                    delay /= 2
                    print('传输速率: {:.2f}MB/s, 延时: {:.3f}ms'.format((len(bytedata) / (1000 * delay)), delay))
                if self.speed_count%20 == 0:
                    self.ui.out_message.appendPlainText('传输速率: {:.2f}MB/s, 延时: {:.3f}ms'.format((len(bytedata) / (1000 * delay)), delay))

    def Shut_Video(self):
        if self.TCPsock != None:
            self.ui.out_message.appendPlainText('TCP已断开连接')
            self.TCPsock.close()
        if self.UDPsock != None:
            self.ui.out_message.appendPlainText('UDP已断开连接')
            self.UDPsock.close()
        cv2.destroyAllWindows()


    def Video_UDP(self):
        # socket.AF_INET 用于服务器与服务器之间的网络通信
        # socket.SOCK_STREAM 代表基于TCP的流式socket通信
        self.UDPsock = socket(AF_INET, SOCK_DGRAM)
        # 连接服务端
        self.address_server = (IP, SERVER_PORT)
        # self.UDPsock.connect(self.address_server)
        # 从摄像头采集图像
        # 参数是0,表示打开笔记本的内置摄像头,参数是视频文件路径则打开视频
        capture = cv2.VideoCapture(0)
        # capture.read() 按帧读取视频
        # ret,frame 是capture.read()方法的返回值
        # 其中ret是布尔值，如果读取帧正确，返回True;如果文件读到末尾，返回False。
        # frame 就是每一帧图像，是个三维矩阵
        ret, frame = capture.read()
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
        th = Thread(target=self.UDP_start, args=(ret,frame, encode_param, capture))
        th.setDaemon(True)
        th.start()

    def UDP_start(self,ret,frame,encode_param,capture):
        while ret:
            # 首先对图片进行编码，因为socket不支持直接发送图片
            # '.jpg'表示把当前图片frame按照jpg格式编码
            # result, img_encode = cv2.imencode('.jpg', frame)
            # 压缩图像
            img_encode = cv2.imencode('.jpg', frame, encode_param)[1]
            # 转换为字节流
            bytedata = img_encode.tobytes()
            # 将输入数据转换为矩阵形式
            # bytearray返回一个新字节数组 读取了图片并显示出来，那么存储的数据格式必须为uint8
            data = numpy.asarray(bytearray(bytedata), dtype="uint8")
            # 解码进行显示
            # bool imencode(const String& ext, InputArray img, vector<uchar>& buf, const vector<int>& params=vector<int>())
            # ext-定义输出文件格式的扩展名 img-需要被编码的图像 buf-输出的缓存区，类型是vector parms-被编码的格式和压缩率,类型是vector 默认使用该种标识。
            # cv2.IMREAD_COLOR加载一张彩色图片，忽视它的透明度。
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            # 载入的图片显示
            cv2.imshow("client_UDP", img)
            # cv2.waitKey(int delay)不断刷新图像，频率为delay，单位是ms，返回值为当前键盘按下的值，没有按键时返回-1.
            c = cv2.waitKey(1)
            # 按下esc退出
            # if c & 0xff == 27:
            #     self.UDPsock.sendto('Close'.encode(),self.address_server)
            #     capture.release()
            #     cv2.destroyAllWindows()
            #     self.UDPsock.close()
            #     break
            stringData = data.tostring()
            # 生成标志数据
            # 首先发送图片编码后的长度
            self.UDPsock.sendto(str(len(stringData)).encode(),self.address_server)

            ret, frame = capture.read()
            cv2.resize(frame, (640, 480))

            # 接收服务端的应答,准备计时
            data_re = self.UDPsock.recv(1024)
            if (data_re.decode() == 'ACK'):
                # 开始计时
                self.speed_count = self.speed_count + 1
                start = time.perf_counter()
                # 服务端已经收到标志数据，开始发送图像字节流数据
                self.UDPsock.sendto(bytedata,self.address_server)
                # 计算发送完成的延时
                data_re,addr = self.UDPsock.recvfrom(1024 * 1024)
                if data_re.decode() == "ACK":
                    end = time.perf_counter()
                    delay = (end - start) * 1000
                    delay /= 2
                    print('传输速率: {:.2f}MB/s, 延时: {:.3f}ms'.format((len(bytedata) / (1000 * delay)), delay))
                if self.speed_count % 20 == 0:
                    self.ui.out_message.appendPlainText('传输速率: {:.2f}MB/s, 延时: {:.3f}ms'.format((len(bytedata) / (1000 * delay)), delay))


app = QApplication([])
stats = Client()
stats.ui.show()
app.exec_()