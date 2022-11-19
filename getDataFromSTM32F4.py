import serial
import numpy as np
import matplotlib.pyplot as plt
from IPython import get_ipython
import time
import math
import threading

#######################################################################################

class SerialThread(threading.Thread):
    def __init__(self, serial_port, length=4):
        threading.Thread.__init__(self)
        self.serial_port = serial_port
        self.serial_read_data = []
        self.length = length
        self.finished = False

    def isFinished(self):
        return self.finished

    def getSerialData(self):
        return self.serial_read_data

    def run(self):
        self.finished = False
        res = serial_portF4.read(self.length)
        line = []
        for c in res:
            line.append(c)
        self.serial_read_data = np.array(line, np.uint8)
        self.finished = True

#######################################################################################

def readUINT32fromSerial(serial_port):
    global SERIAL_READ_DATA
    SERIAL_READ_DATA = []
    res = serial_port.read(4)
    line = []
    for c in res:
        line.append(c)
    arr = np.array(line, np.uint8)
    res = arr.view(np.uint32)[0]
    SERIAL_READ_DATA = res
    return res
#######################################################################################

def int32_to_int8(n):
    n = int(n)
    mask = (1 << 8) - 1
    return [(n >> k) & mask for k in range(0, 32, 8)]
#######################################################################################

def int16_to_int8(n):
    n = int(n)
    mask = (1 << 8) - 1
    return [(n >> k) & mask for k in range(0, 16, 8)]
#######################################################################################

def send4BytesToSerial(serial_port, dataList):
    readSerialThread = SerialThread(serial_port, 4)
    readSerialThread.start()
    serial_port.write(dataList)
    while not readSerialThread.isFinished():
        pass
    # res = readUINT32fromSerial(serial_port)
    return []

#######################################################################################

serial_portF4 = serial.Serial(
port='/dev/ttyACM1',
baudrate=115200,
parity=serial.PARITY_NONE,
stopbits=serial.STOPBITS_ONE,
bytesize=serial.EIGHTBITS,
timeout=0.1)
print("connected to: " + serial_portF4.portstr)

readSerialThread = SerialThread(serial_portF4, 20000)

serial_portF4.write(np.array(int16_to_int8(1), np.uint8))
time.sleep(.01)
serial_portF4.write(np.array(int16_to_int8(1), np.uint8))  # start write
time.sleep(1)
readSerialThread.start()
serial_portF4.write(np.array(int16_to_int8(2), np.uint8))  # get data
while not readSerialThread.isFinished():
    pass

serial_data = readSerialThread.getSerialData()
res = serial_data.view(np.float32)

# line=[]
# while not flag:
#     for c in serial_port.read():
#         line.append(c)
#         print(''+str(c))
#         if len(line) == 10:
#             arr = np.array(line, np.uint8)
#             arr = arr.view(np.int16)
#             flag=True
#             break

serial_portF4.close()
pass






# arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(getREG([MC_REG_STOPLL_EL_ANGLE, MC_REG_SPEED_REF])))
# data = decodeRegValues(arr, [MC_REG_STOPLL_EL_ANGLE, MC_REG_SPEED_REF])


# FFOC = 2000
# elToMech = 7
# contElAngle = np.zeros(len(elAngle))
# counter=0
# for i in range(len(elAngle)-1):
#     contElAngle[i] = elAngle[i]-(-2**15)+(2**16)*counter
#     if elAngle[i+1]<elAngle[i]:
#         counter += 1
# angleFromEl = contElAngle/elToMech/(2**16)*360
# elVelHz = np.diff(angleFromEl)*FFOC/360*10

# inds = range(0,300)
# plt.plot(contElAngle[inds]-contElAngle[inds[0]], speedRef[inds])
# plt.plot(contElAngle[inds]-contElAngle[inds[0]], elVelHz[inds])
# plt.grid(True)
# plt.show()

    # time.sleep(2)
    # decodeCommandResult(sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(START_STOP[0]))))
    # time.sleep(5)
    # decodeCommandResult(sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(START_STOP[0]))))

    # arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(setREG(
    #     [MC_REG_CONTROL_MODE, MC_REG_SPEED_KP, MC_REG_SPEED_REF], [STC_SPEED_MODE, 500, 300])))
    # arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(getREG(
    #     [MC_REG_CONTROL_MODE,  MC_REG_SPEED_KP, MC_REG_SPEED_REF])))
    # decodeRegValues(arr, [MC_REG_CONTROL_MODE,  MC_REG_SPEED_KP, MC_REG_SPEED_REF])
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(GET_MCP_VERSION[0]))), GET_MCP_VERSION[1])
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(START_MOTOR[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(STOP_RAMP[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(STOP_MOTOR[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(FAULT_ACK[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(IQDREF_CLEAR[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(PFC_ENABLE[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(PFC_DISABLE[0]))))
    # time.sleep(.1)
    # decodeCommandResult(sendManyBytesToSerial(ser, createDATA_PACKET(getCOMMAND(PFC_FAULT_ACK[0]))))


   # ser.write(getByteArray([0x09, 0x00, 0x00]))

#     while not flag:
#         for c in ser.read():
#             line.append(c)
#             print(''+str(c))
#             if len(line) == 6144:
#                 arr = np.array(line, np.uint8)
#                 arr = arr.view(np.int16)
#                 flag=True
#                 break
