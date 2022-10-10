import can

def CanToTcpMessage(canMessage):
    # tcp: [ID],[RTR],[IDE],[DATABYTES 0..8B]\n
    rtr = "00" # remote trasmit request
    ide = "00" # id extended

    if canMessage.is_extended_id:
        ide = "01"
    if canMessage.is_remote_frame:
        rtr = "01"

    msg = "%s,%s,%s," % (hex(canMessage.arbitration_id),rte,ide)
    for byte in canMessage.data:
        if len(hex(byte)) == 3:
            msg += "0"
        msg +=  hex(byte)

    msg += '\n'
    return msg.replace("0x", "").encode()

def TcpToCanMessage(tcpMessage):
    extendedId = False
    remoteRequest = False

    tcpMessage = tcpMessage[:-1] # remove \n
    sp = tcpMessage.decode().split(",")

    id=int(sp[0], 16)
    data = bytes.fromhex(sp[3])
    if sp[1] != "00":
        remoteRequest = True
    if sp[2] != "00":
        extendedId = True

    return can.Message(arbitration_id=id, data=data, is_extended_id=extendedId, is_remote_frame=remoteRequest)