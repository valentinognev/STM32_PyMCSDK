import serial
import math
import time
from bg431Communication import *

#######################################################################################
#######################################################################################

# comm = getCOMMAND(command=GET_MCP_VERSION)
# createDATA_PACKET(comm)
# pack = createDATA_PACKET(setREG(
#     [MC_REG_CONTROL_MODE, MC_REG_SPEED_KP, MC_REG_SPEED_REF], [STC_SPEED_MODE, 500, 300]))
# baudrate=1843200,\
serial_port = serial.Serial(
port='/dev/ttyACM0',\
baudrate=1843200,\
parity=serial.PARITY_NONE,\
stopbits=serial.STOPBITS_ONE,\
bytesize=serial.EIGHTBITS,\
timeout=0.1)
print("connected to: " + serial_port.portstr)

#this will store the line

#version, DATA_CRC, RX_maxSize, TXS_maxSize, TXA_maxSize = decodeBEACON(send4BytesToSerial(serial_port, getBEACON()))
version, DATA_CRC, RX_maxSize, TXS_maxSize, TXA_maxSize = decodeBEACON(send4BytesToSerial(serial_port, getBEACON(version=0, RX_maxSize=3, TXS_maxSize=3, TXA_maxSize=32)))
time.sleep(.1)
packetNumber, ipID, cbit, Nbit = decodePING(send4BytesToSerial(serial_port, getPING(packetNumber=0)))
time.sleep(.1)
speedKp=20000
speedKpDiv = 2048/8
speedKi=6000
speedKiDiv = 16384
speedKd=0
speedKdDiv = 16
arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(setREG([MC_REG_SPEED_KP,MC_REG_SPEED_KI,MC_REG_SPEED_KD,
                                                                   MC_REG_SPEED_KP_DIV, MC_REG_SPEED_KI_DIV, MC_REG_SPEED_KD_DIV], 
                                                                  [speedKp, speedKi, speedKd, 
                                                                  math.log2(speedKpDiv), math.log2(speedKiDiv), math.log2(speedKdDiv)])))
time.sleep(.1)
# arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(getREG([MC_REG_SPEED_KP,  MC_REG_SPEED_KI, MC_REG_SPEED_KD,
#                                                                    MC_REG_SPEED_KP_DIV, MC_REG_SPEED_KI_DIV, MC_REG_SPEED_KD_DIV])))  # set speed PID values
# data = decodeRegValues(arr, [MC_REG_SPEED_KP,  MC_REG_SPEED_KI, MC_REG_SPEED_KD, 
#                              MC_REG_SPEED_KP_DIV, MC_REG_SPEED_KI_DIV, MC_REG_SPEED_KD_DIV])
# time.sleep(.1)

decodeCommandResult(sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(START_MOTOR[0]))))
# time.sleep(10)

rpmmeanarr =      [2500, 2600, 2700, 2800, 2900, 3000, 2900, 2800, 2700, 2600]#[1800, 2500, 2000, 1600, 3000, 2500, 1900, 2100, 2300, 1800]
rpmDoubleAmparr = [ 300,  300,  300,  300,  300,  300,  300,  300,  300,  300]#[100,   300,  200,  200,  300,  100,  150,  180,  200,  100]
phaserr =         [10,    180,  270,   90,  135,  224,  355,    0,   25,   74]
rpmmean = 2500
rpmDoubleAmp = 200
phase = 0

while True:
    with keyboard.Events() as events:
        # Block for as much as possible
        event = events.get(1e6)
    if event.key == keyboard.KeyCode.from_char('n'):
        sinParams = np.append(np.append(int32_to_int8(rpmmean),int16_to_int8(0)),int16_to_int8(0))
    elif event.key == keyboard.KeyCode.from_char('q'):
        break
    elif str(event.key) == 'Key.up' or event.key == keyboard.KeyCode.from_char('w'):
        sinParams = np.append(np.append(int32_to_int8(rpmmean),int16_to_int8(rpmDoubleAmp)),int16_to_int8(90))
        print('Key up\n')
    elif str(event.key) == 'Key.down' or event.key == keyboard.KeyCode.from_char('s'):
        sinParams = np.append(np.append(int32_to_int8(rpmmean),int16_to_int8(rpmDoubleAmp)),int16_to_int8(270))
        print('Key down\n')
    elif str(event.key) == 'Key.left' or event.key == keyboard.KeyCode.from_char('a'):
        sinParams = np.append(np.append(int32_to_int8(rpmmean),int16_to_int8(rpmDoubleAmp)),int16_to_int8(180))
        print('Key left\n')
    elif str(event.key) == 'Key.right' or event.key == keyboard.KeyCode.from_char('d'):
        sinParams = np.append(np.append(int32_to_int8(rpmmean),int16_to_int8(rpmDoubleAmp)),int16_to_int8(0))
        print('Key right\n')
    arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(setREG([MC_REG_SPEED_SIN],[sinParams])))   # Set sin

# for i in range(10):
#     sinParams = np.append(np.append(int32_to_int8(rpmmeanarr[i]),int16_to_int8(rpmDoubleAmparr[i])),int16_to_int8(phaserr[i]))
#     arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(setREG([MC_REG_SPEED_SIN],[sinParams])))   # Set sin
#     time.sleep(.1)
res = sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(STOP_MOTOR[0])))                # Stop motor
# decodeCommandResult(res)
# time.sleep(.5)
# arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(GET_DBG_DATA[0])))
# arr = arr.view(np.int16)

# angle = arr[:1024]
# tarSpeed = arr[1024:2048]
# elangle = arr[2048:3072]
# encoderAngle = arr[3072:]

# SPEED_LOOP_FREQUENCY_HZ = 1000
# elToMech = 12

# contAngle = np.zeros(len(angle))
# counter=0
# for i in range(len(angle)-1):
#     contAngle[i] = angle[i]-(-2**15)+(2**16)*counter
#     if angle[i+1]<angle[i]:
#         counter += 1
# contAngle = contAngle/(2**16)*360
# contAngleVelHz = np.diff(contAngle)*SPEED_LOOP_FREQUENCY_HZ/360*10
# contAngleVelHz[contAngleVelHz>1000]=500








# contElAngle = np.zeros(len(elangle))
# counter=0;
# for i in range(len(elangle)-1):
#     contElAngle[i] = elangle[i]-(-2**15)+(2**16)*counter
#     if elangle[i+1]<elangle[i]:
#         counter += 1
# angleFromEl = contElAngle/elToMech/(2**16)*360
# elVelHz = np.diff(angleFromEl)*FFOC/360*10

# inds = range(0,900)
# plt.subplot(2,1,1)
# plt.plot(contAngle[inds]-contAngle[inds[0]],tarSpeed[inds]/10*60,'x-')
# plt.plot(contAngle[inds]-contAngle[inds[0]],contAngleVelHz[inds]/10*60,'-o')
# plt.ylabel('RPM')
# plt.xlabel('angle [deg]')
# plt.grid(True)
# plt.subplot(2,1,2)
# plt.plot(encoderAngle)
# plt.show()
# #plt.pause(0.0001)
# #input("Press Enter to continue...")

serial_port.close()
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
    
