#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket

class TcpClient:
    BUFSIZE = 2048 
    data_processor = None

    def __init__(self, ip, port):
        self.HOST = ip
        self.PORT = port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ADDR = (self.HOST, self.PORT)
        self.client.connect(self.ADDR)
        self.socket_fd = self.client.makefile('rw', 0)

    '''
    设置数据处理的回调函数: func(line)
    '''
    def SetDataProcessor(self, func):
        self.data_processor = func

    def Recv(self):
        try:
            buf = self.client.recv(2048)
        except socket.error, e:
            print "[tcp_client] Error receiving data: %s" %e
            self.client.close()
            return -1

        if not len(buf):
            print "socket has been closed"
            self.client.close()
            return -1

        #print ">>> %s" %buf 
        # 验证数据合法性, 并使用数据处理函数对数据进行计算
        lines = buf.split("\n")
        for line in lines:
            if len(line) == 0:
                continue
            items = line.split("\t")
            if len(items) >= 2 and "ctpdata" == items[0]:
                result = self.data_processor(items[1])

                if "" != result:
                    ret = self.Send(result)
                    if 0 != ret:
                        print "[tcp_client] Error: Send result to TcpTrader fail."
            else:
                print "[tcp_client] Recv Data Format Error: %s" %line 

        return 0

    def Send(self, line):
        try:
            self.client.send("%s\n" %line)
            self.socket_fd.flush()
        except socket.error, e:
            print "Error sending data: %s" %e
            self.client.close()
            return -1
        return 0

    def Run(self):
        while True:
            ret = self.Recv()
            if 0 != ret:
                print "[tcp_client] Error: Recv() fail."
                break

