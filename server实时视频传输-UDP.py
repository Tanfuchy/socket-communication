#!/usr/bin/python
# -*-coding:utf-8 -*-

import socket
import cv2
import numpy as np

# socket.AF_INET IPv4协议
# socket.SOCK_STREAM 代表基于TCP的流式socket通信
# TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.SOCK_DGRAM 代表基于UDP的流式socket通信
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 设置地址与端口，如果是接收任意ip对本服务器的连接，地址栏可空，但端口必须设置
IP = ''
PORT = 50000
BUFLEN = 60000
UDPsocket.bind((IP, PORT))

while True:
    # 循环接收每一帧数据
    length, addr = UDPsocket.recvfrom(1024)  # 首先接收来自客户端发送的大小信息
    length = length.decode()
    # 数据包小于60000，可以直接发送
    if int(length) != 0:
        # 确认已经接受数据长度
        UDPsocket.sendto('ACK'.encode(), addr)
        # 接收整张图片
        bytedata, addr = UDPsocket.recvfrom(BUFLEN)
        # 接收完一帧数据
        UDPsocket.sendto('ACK'.encode(), addr)
        img = np.asarray(bytearray(bytedata), dtype="uint8")
        # 解码进行显示
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        cv2.imshow("server", img)
        if cv2.waitKey(1) == 27:
            break


# TCPsocket.close()
UDPsocket.close()
cv2.destroyAllWindows()
