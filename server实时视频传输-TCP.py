#!/usr/bin/python
# -*-coding:utf-8 -*-

import socket
import cv2
import numpy as np
# socket.AF_INET IPv4协议
# socket.SOCK_STREAM 代表基于TCP的流式socket通信
TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 设置地址与端口，如果是接收任意ip对本服务器的连接，地址栏可空，但端口必须设置
IP = ''
PORT = 50000
BUFLEN = 60000
# 将Socket（套接字）绑定到地址
TCPsocket.bind((IP, PORT))
# 最多监听10个端口
TCPsocket.listen(10)

print('Waiting for videos...')


# 接受TCP连接并返回，其中conn是新的套接字对象，可以用来接收和发送数据，addr是链接客户端的地址。
conn, addr = TCPsocket.accept()
while True:
    # 循环接收每一帧数据
    length = conn.recv(1024).decode()
    print(length)  # 首先接收来自客户端发送的大小信息
    if length == "Close":
        break
    if length != 0:
        # 确认已经接受数据长度
        conn.send('ACK'.encode())
        # 接收整张图片
        bytedata = conn.recv(BUFLEN)
        img = np.asarray(bytearray(bytedata), dtype="uint8")
        # 解码进行显示
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        cv2.imshow("server", img)
        conn.send('ACK'.encode())
        if cv2.waitKey(1) == 27:
            break

TCPsocket.close()
cv2.destroyAllWindows()
