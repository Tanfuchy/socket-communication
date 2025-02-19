#  回环地址服务端
# TCP/IP
# 导入socket 库
from socket import *

# 主机地址为空字符串，表示绑定本机所有网络接口ip地址
IP = '127.0.0.1'
# 端口号
PORT = 50000
# 定义一次从socket缓冲区最多读入1024个字节数据
BUFLEN = 1024

# 实例化一个socket对象
# 参数 AF_INET 表示该socket网络层使用IP协议
# 参数 SOCK_STREAM 表示该socket传输层使用tcp协议
serverSocket = socket(AF_INET, SOCK_STREAM)

# socket绑定地址和端口
serverSocket.bind((IP, PORT))

# 使socket处于监听状态，等待客户端的连接请求
# 最多接受8个等待连接的客户端
serverSocket.listen(8)
print('服务端启动成功，在' + str(PORT) + '端口等待客户端连接...')
# 此处采用阻塞式监听
dataSocket, addr = serverSocket.accept()
print('接受一个客户端连接:', addr)

while True:
    # BUFLEN 指定从接收缓冲里最多读取多少字节
    recved = dataSocket.recv(BUFLEN)
    # 如果返回空bytes，表示对方关闭了连接
    # 退出循环，结束消息收发
    if not recved:
        break
    # 读取的字节数据是bytes类型，需要解码为字符串
    info = recved.decode()
    print('收到客户端信息: ' + info)

    # 发送的数据类型必须是bytes，所以要编码
    dataSocket.send(('服务端返回信息: ' + info).encode())

# 服务端也调用close()关闭socket
dataSocket.close()
serverSocket.close()
