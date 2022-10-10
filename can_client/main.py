import os
import serial
import socket
import time
from threading import Thread


# TCP Client
#HOST = "192.168.1.234"
#PORT = 9001
HOST = "192.168.1.21"
PORT = 50002
# TTY
SERIAL_BAUDRATE = 25000
COM_INPUT = "/dev/ttyCanIn"
COM_SINK = "/dev/ttyS1234"


def main():
    com = serial.Serial(COM_INPUT, SERIAL_BAUDRATE)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        thSender = Thread(target=sender,args=(s,com))
        thSender.start()

        while True:
            data = s.recv(1024)
            if data == None or data == "".encode():
                print("disconnected")
                break
            print("data up: ", data)
            com.write(data)

        thSender.join()

def sender(s, com):
    while True:
        data = com.readline()
        print("data down: ", data)
        s.send(data)

def configSerialBridge(com1Name, com2Name):
    os.system('nohup sudo socat PTY,link='+com1Name+',raw,echo=0 PTY,link='+com2Name+',raw,echo=0 > /dev/null &')
    time.sleep(1)
    os.system('sudo chmod 777 /dev/ttyCanIn && sudo chmod 777 /dev/ttyS1234')

if __name__ == "__main__":
    configSerialBridge(COM_INPUT, COM_SINK)
    main()
