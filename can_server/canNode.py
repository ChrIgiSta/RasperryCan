import can
import os
from threading import Thread
import queue

TX_TIMEOUT = 10.0

class CanNode:
    can = None
    qCanTx = None
    qCanRx = None
    interrupted = False

    def __init__(self, channel, qCanRx, qCanTx, initOs = False, canSpeed=10000):
        if initOs:
            os.system('sudo ip link set '+channel+' type can bitrate ' + str(canSpeed))
            os.system('sudo ifconfig '+can0+' up')

        self.can = can.interface.Bus(channel = channel, bustype = 'socketcan')
        self.qCanTx = qCanTx
        self.qCanRx = qCanRx
        self.initOs = initOs

    def start(self):
        self.listenerThread = Thread(target=self.listenForever)
        self.listenerThread.start()

    def listenForever(self):
        senderThread = Thread(target=self.sender)
        senderThread.start()

        while not self.interrupted:
            msg = self.can.recv(TX_TIMEOUT)
            if msg != None:
                self.qCanRx.put(msg)
        senderThread.join()

    def sender(self):
        while not self.interrupted:
            msg = self.qCanTx.get()
            self.can.send(msg)
    
    def stop(self):
        self.interrupted = True
        self.listenerThread.join()

    def deinit(self):
        if self.initOs:
            os.system('sudo ifconfig '+can0+' down')
