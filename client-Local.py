# 回环地址客户端
# TCP/IP
from socket import *

# CLIENT_IP = '127.0.0.1'
# CLIENT_PORT = 20000
SERVER_IP = '127.0.0.1'
SERVER_PORT = 50000
BUFLEN = 1024

# 实例化一个socket对象，指明协议
clientSocket = socket(AF_INET, SOCK_STREAM)
# 连接服务端socket
clientSocket.connect((SERVER_IP, SERVER_PORT))

while True:
    # 从终端读入用户输入的字符串
    toSend = input('输入要发送的信息: ')
    if toSend == 'quit':
        break
    # 发送消息，也要编码为 bytes
    clientSocket.send(toSend.encode())
    # 等待接收服务端的消息
    recved = clientSocket.recv(BUFLEN)
    # 如果返回空bytes，表示对方关闭了连接
    if not recved:
        break
    # 打印读取的信息
    print(recved.decode())

clientSocket.close()
