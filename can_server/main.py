from tcpServer import TcpServer
from canNode import CanNode
from message import CanToTcpMessage, TcpToCanMessage
import time
import queue
from threading import Thread
import can

def main():

    qTcpTx = queue.Queue()
    qTcpRx = queue.Queue()
    qCanTx = queue.Queue()
    qCanRx = queue.Queue()

    ok = selfTest()
    if not ok:
        print("selftest failed")
        exit(-1)

    print("start can to tcp bridge")
    tcpServer = TcpServer(qTcpRx, qTcpTx)
    tcpServer.start()

    canNode = CanNode("can0", qCanRx, qCanTx)
    canNode.start()

    thCan2Tcp = Thread(target=canToTcp,args=(qCanRx, qTcpTx,))
    thCan2Tcp.start()
    thTcp2Can = Thread(target=tcpToCan,args=(qTcpRx, qCanTx,))
    thTcp2Can.start()

    while True:
        time.sleep(1)
        # todo: catch os signals and shutdown graceful

    tcpServer.stop()
    canNode.stop()
    canNode.deinit()

    thTcp2Can.join()
    thCan2Tcp.join()
  
    print("exit")

def selfTest():
    canMsg = can.Message(arbitration_id=0x0102, data=[0x11,0x02,0x04,0x05], is_extended_id=False)
    tcpMsg = CanToTcpMessage(canMsg)
    print(tcpMsg)
    canNew = TcpToCanMessage(tcpMsg)
    print(canNew)

    # if canMsg. != canNew:
    #     return False

    return True



def canToTcp(qCanRx, qTcpTx):
    while True:
        canMsg = qCanRx.get()
        print("CAN TO TCP", canMsg)
        tcpMsg = CanToTcpMessage(canMsg)
        print(tcpMsg)
        qTcpTx.put(tcpMsg)

def tcpToCan(qTcpRx, qCanTx):
    while True:
        tcpMsg = qTcpRx.get()
        print("TCP TO CAN", tcpMsg)
        if tcpMsg != "".encode():
            canMsg = TcpToCanMessage(tcpMsg)
            print("write to can: ", canMsg)
            qCanTx.put(canMsg)

if __name__ == "__main__":
    main()