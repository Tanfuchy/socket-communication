#!/usr/bin/python
# -*-coding:utf-8 -*-
import socket
import cv2
import numpy
import time

# socket.AF_INET 用于服务器与服务器之间的网络通信
# socket.SOCK_STREAM 代表基于TCP的流式socket通信
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 连接服务端
IP = '127.0.0.1'
PORT = 50000
address_server = (IP, PORT)
sock.connect(address_server)

# 从摄像头采集图像
# 参数是0,表示打开笔记本的内置摄像头,参数是视频文件路径则打开视频
capture = cv2.VideoCapture(0)
# capture.read() 按帧读取视频
# ret,frame 是capture.read()方法的返回值
# 其中ret是布尔值，如果读取帧正确，返回True;如果文件读到末尾，返回False。
# frame 就是每一帧图像，是个三维矩阵
ret, frame = capture.read()
encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
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
    cv2.imshow("client", img)
    # cv2.waitKey(int delay)不断刷新图像，频率为delay，单位是ms，返回值为当前键盘按下的值，没有按键时返回-1.
    c = cv2.waitKey(1)
    # 按下esc退出
    if c & 0xff == 27:
        sock.send('Close'.encode())
        capture.release()
        cv2.destroyAllWindows()
        sock.close()
        break
    stringData = data.tostring()
    # 生成标志数据
    # 首先发送图片编码后的长度
    sock.send(str(len(stringData)).encode())

    ret, frame = capture.read()
    cv2.resize(frame, (640, 480))

    # 接收服务端的应答,准备计时
    data_re = sock.recv(1024)
    if (data_re.decode() == 'ACK'):
        # 开始计时
        start = time.perf_counter()
        # 服务端已经收到标志数据，开始发送图像字节流数据
        sock.send(bytedata)
        # 计算发送完成的延时
        data_re = sock.recv(1024 * 1024)
        if data_re.decode() == "ACK":
            end = time.perf_counter()
            delay = (end - start) * 1000
            delay /= 2
            print('传输速率: {:.2f}MB/s, 延时: {:.3f}ms'.format((len(bytedata) / (1000 * delay)), delay))

sock.close()
cv2.destroyAllWindows()
