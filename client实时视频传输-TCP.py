#!/usr/bin/python
# -*-coding:utf-8 -*-
# =========================实时视频传输: 客户端、TCP协议传输========================

import cv2
import time
from socket import *
import numpy as np

# 服务端ip地址
SERVER_IP = '10.35.155.81'
# 服务端端口号
PORT = 50000
RECV_BUFLEN = 1024
# socket.AF_INET IPv4协议
# socket.SOCK_STREAM 代表基于TCP的流式socket通信
TCPclient = socket(AF_INET, SOCK_STREAM)
# 连接服务器
TCPclient.connect((SERVER_IP, PORT))
# 从摄像头采集图像
# 参数是0,表示打开笔记本的内置摄像头, 参数是视频文件路径则打开视频
cap = cv2.VideoCapture(0)

encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
while True:

    # cap.read() 按帧读取视频
    # ret,frame 是capture.read()方法的返回值
    # 其中ret是布尔值，如果读取帧正确，返回True;如果文件读到末尾，返回False
    # frame 就是每一帧图像，是个三维矩阵
    ref, frame = cap.read()
    # 压缩图像
    img_encode = cv2.imencode('.jpg', frame, encode_param)[1]
    # 转换为字节流
    bytedata = img_encode.tobytes()
    # 将输入数据转换为矩阵形式
    # bytearray返回一个新字节数组 读取了图片并显示出来，那么存储的数据格式必须为uint8
    img = np.asarray(bytearray(bytedata), dtype="uint8")
    # 解码进行显示
    # bool imencode(const String& ext, InputArray img, vector<uchar>& buf, const vector<int>& params=vector<int>())
    # ext-定义输出文件格式的扩展名 img-需要被编码的图像 buf-输出的缓存区，类型是vector parms-被编码的格式和压缩率,类型是vector 默认使用该种标识。
    # cv2.IMREAD_COLOR加载一张彩色图片，忽视它的透明度。
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    # 载入的图片显示
    cv2.imshow("client", img)
    # cv2.waitKey(int delay)不断刷新图像，频率为delay，单位是ms，返回值为当前键盘按下的值，没有按键时返回-1.
    c = cv2.waitKey(1)
    # 按下esc退出
    if c & 0xff == 27:
        TCPclient.send('Close'.encode())
        cap.release()
        cv2.destroyAllWindows()
        TCPclient.close()
        break

    # ==========完成一帧的数据处理后开始发送数据==========
    # 生成标志数据
    ori_data = str(len(bytedata))
    flag_data = ori_data.encode()
    TCPclient.send(flag_data)
    # 接收服务端的应答
    data = TCPclient.recv(RECV_BUFLEN)
    if (data.decode() == 'ACK'):
        # 开始计时
        start = time.perf_counter()
        # 服务端已经收到标志数据，开始发送图像字节流数据
        TCPclient.send(bytedata)
        # 计算发送完成的延时
        data = TCPclient.recv(1024*1024)
        if data.decode() == "ACK":
            end = time.perf_counter()
            delay = (end - start) * 1000
            delay /= 2
            print('传输速率: {:.2f}MB/s, 延时: {:.3f}ms'.format((len(bytedata) / (1000 * delay)), delay))