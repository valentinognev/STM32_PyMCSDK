import serial
import math
import time
from bg431Communication import *


def intAngleToContinousAngle(angle: np.array, minValue: int, valSize: int) -> np.array:
    contAngle = np.zeros(len(angle))
    counter = 0
    for i in range(len(angle)-1):
        contAngle[i] = angle[i] - minValue + valSize*counter
        if angle[i+1] < angle[i]:
            counter += 1
    contAngle = contAngle/valSize*360
    return contAngle

# comm = getCOMMAND(command=GET_MCP_VERSION)
# createDATA_PACKET(comm)
# pack = createDATA_PACKET(setREG(
#     [MC_REG_CONTROL_MODE, MC_REG_SPEED_KP, MC_REG_SPEED_REF], [STC_SPEED_MODE, 500, 300]))
# baudrate=1843200,\
serial_portBG431 = serial.Serial(
port='/dev/ttyACM0',\
baudrate=1843200,\
parity=serial.PARITY_NONE,\
stopbits=serial.STOPBITS_ONE,\
bytesize=serial.EIGHTBITS,\
timeout=0.1)
print("connected to: " + serial_portBG431.portstr)

#this will store the line

version, DATA_CRC, RX_maxSize, TXS_maxSize, TXA_maxSize = decodeBEACON(send4BytesToSerial(serial_portBG431, getBEACON(version=0, RX_maxSize=3, TXS_maxSize=3, TXA_maxSize=32)))
time.sleep(.1)
packetNumber, ipID, cbit, Nbit = decodePING(send4BytesToSerial(serial_portBG431, getPING(packetNumber=0)))
time.sleep(.1)

constant1_q = 0  # Feed forward q constant
constant1_d = 0  # Feed forward d constant
constant2_qd = 2   # Feed forward constant

torquestart = 200
torquemean = 200
torqueDoubleAmp = 0

torquemeanarr =      np.array([100, 2600, 2700, 2800, 2900, 3000, 2900, 2800, 2700, 2600])*0+torquemean#[1800, 2500, 2000, 1600, 3000, 2500, 1900, 2100, 2300, 1800]
torqueDoubleAmparr = np.array([ 50,  50,  50,  50,  300,  300,  300,  300,  300,  300])*0+torqueDoubleAmp#[100,   300,  200,  200,  300,  100,  150,  180,  200,  100]
phaserr =         np.array([10,    180,  270,   90,  135,  224,  355,    0,   25,   74])*0


# arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_CONTROL_MODE], [[MCM_TORQUE_MODE]])))

decodeCommandResult(sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getCOMMAND(START_MOTOR[0]))))
sinParams = np.append(np.append(int32_to_int8(torquestart),int16_to_int8(0)),int16_to_int8(0))
arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_TORQUE_SIN],[sinParams])))   # Set sin
time.sleep(1)
sinParams = np.append(np.append(int32_to_int8(torquemean),int16_to_int8(torqueDoubleAmp)),int16_to_int8(0))
arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_TORQUE_SIN],[sinParams])))   # Set sin
time.sleep(1)

arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_DBG_START_WRITE],[[]])))    # Start Write
time.sleep(.01)
for i in range(10):
    sinParams = np.append(np.append(int32_to_int8(torquemeanarr[i]),int16_to_int8(torqueDoubleAmparr[i])),int16_to_int8(phaserr[i]))
    arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_SPEED_SIN],[sinParams])))   # Set sin
    time.sleep(.1)
res = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getCOMMAND(STOP_MOTOR[0])))                # Stop motor
decodeCommandResult(res)
time.sleep(.5)
arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getCOMMAND(GET_DBG_DATA[0])))
arr = arr.view(np.int16)

angle = arr[:1024]
tarSpeed = arr[1024:2048]
elangle = arr[2048:3072]
encoderAngle = arr[3072:]

SPEED_LOOP_FREQUENCY_HZ = 1000
elToMech = 7

mecContAngle = intAngleToContinousAngle(angle, -2**15, 2**16)
contMecAngleSpeedHz = np.diff(mecContAngle)*SPEED_LOOP_FREQUENCY_HZ/360

elContAngle = intAngleToContinousAngle(elangle, -2**15, 2**16)/elToMech
contElAngleSpeedHz = np.diff(elContAngle)*SPEED_LOOP_FREQUENCY_HZ/360

encContAngle = intAngleToContinousAngle(encoderAngle, 0, 2000)
contEncAngleSpeedHz = np.diff(encContAngle)*SPEED_LOOP_FREQUENCY_HZ/360

inds = range(0,900)
#plt.plot(contAngle[inds]-contAngle[inds[0]],tarSpeed[inds]/10*60,'x-')
plt.plot(mecContAngle[inds]-mecContAngle[inds[0]],contEncAngleSpeedHz[inds]*60,'-bo')
plt.plot(elContAngle[inds]-elContAngle[inds[0]],contElAngleSpeedHz[inds]*60,'-x')
plt.plot(encContAngle[inds]-encContAngle[inds[0]],contEncAngleSpeedHz[inds]*60,'--')
plt.ylabel('RPM')
plt.xlabel('angle [deg]')
plt.grid(True)
plt.show()
#plt.pause(0.0001)
#input("Press Enter to continue...")

serial_portBG431.close()
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
    