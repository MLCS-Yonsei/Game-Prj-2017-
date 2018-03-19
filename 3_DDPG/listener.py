import time
import json

from socket import *
csock = socket(AF_INET, SOCK_DGRAM)
csock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
csock.bind(('', 6001))

status = False

i = 0
while True:
    if status == False:
        csock.sendto('Connect'.encode(), ('',54545)) # 대상 서버 , 목적지 포트
        s, addr = csock.recvfrom(1024)
        print('Connected!')
        status = True
    else:
        i = i + 1
        print(i / 10000)
        controlState = {
            'acc': False,
            'brake': False,
            'steer': i / 200
        }
        json_str = json.dumps(controlState)

        csock.sendto(json_str.encode(), ('',54545)) # 대상 서버 , 목적지 포트
