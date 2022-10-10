import socket, select
from threading import Thread
import queue

RECV_BUFFER = 4096

class TcpServer:

    clientList = []
    serverSocket = None
    listenerThread = None
    interrupted = False

    def __init__(self, qTcpRx, qTcpTx):
        self.qTcpTx = qTcpTx
        self.qTcpRx = qTcpRx

    def start(self, host="", port=9001):
             
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((host, port))
        self.serverSocket.listen(10)
     
        print("TCP Server UP and listening on %s@%d " % (host, port))

        self.listenerThread = Thread(target=self.tcpListenForver)
        self.listenerThread.start()
    
    def tcpListenForver(self):
        clientHandlers = []

        while not self.interrupted:
            clientSocket, addr = self.serverSocket.accept()
            self.clientList.append(clientSocket)
            print("Client (%s, %s) connected" % addr)
            clientHandle = Thread(target=self.tcpClientHandler, args=(clientSocket,addr,))
            clientHandle.start()
            clientHandlers.append(clientHandle)

        for c in clientHandlers:
            c.join()

        print("tcpListenForever exited")

    def tcpClientHandler(self, clientSocket, addr):
        try:
            clientSenderThread = Thread(target=self.tcpSender, args=(clientSocket,))
            clientSenderThread.start()
            while not self.interrupted:
                data = clientSocket.recv(RECV_BUFFER)
                if data == None or data == str.encode(""):
                    raise Exception('tcp', 'disconnect or bad data')
                self.qTcpRx.put(data)
        except:
            print("Client (%s, %s) disconected" % addr)
            self.clientList.remove(clientSocket)
            clientSocket.close()

        self.qTcpRx.put(str.encode(""))
        clientSenderThread.join()

    def tcpSender(self, clientSocket):
        try:
            while not self.interrupted:
                tx = self.qTcpTx.get()
                clientSocket.send(tx)
        except:
            print("exception in tcp sender. exiting")

    
    def stop(self):
        self.interrupted = True
        self.serverSocket.close()
        self.listenerThread.join()
        print("tcp server interrupted and stopped")
