import serial
import math
import time
from bg431Communication import *
from joysticInput import *

DEBUG = False

if not DEBUG:
    serial_portBG431 = serial.Serial(
    port='/dev/ttyACM0',\
    baudrate=1843200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0.1)
    print("connected to: " + serial_portBG431.portstr)

if not DEBUG:
    #version, DATA_CRC, RX_maxSize, TXS_maxSize, TXA_maxSize = decodeBEACON(send4BytesToSerial(serial_port, getBEACON()))
    version, DATA_CRC, RX_maxSize, TXS_maxSize, TXA_maxSize = decodeBEACON(send4BytesToSerial(serial_portBG431, getBEACON(version=0, RX_maxSize=3, TXS_maxSize=3, TXA_maxSize=32)))
    time.sleep(.1)
    packetNumber, ipID, cbit, Nbit = decodePING(send4BytesToSerial(serial_portBG431, getPING(packetNumber=0)))
    time.sleep(.1)

torquemean = 2000 # 3000
torqueDoubleAmp = 4000 # 4500
phase = 0
speedFac = 1.1
TORQUEMAX = 3400
TORQUEMIN = 1000
AMPMAX = 4000
AMPMIN = 100

if not DEBUG:
    sinParams = np.append(np.append(int32_to_int8(torquemean),int16_to_int8(torqueDoubleAmp)),int16_to_int8(phase))
    arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_TORQUE_SIN],[sinParams])))   # Set sin

workState = False
oldWorkState = False
# button = NintendoPadIDs()
button = GamePadPlusV3()
controller = ControllerInput()
oldevent = controller.lastEvent
doit = False
while True:
    controller.checkEvents()
    pad = controller.pad
    event = controller.lastEvent
    print('Event '+str(event.type)+' '+str(event.value))
    time.sleep(0.1)

    if pad.button[button['home'][2]]:
        arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getREG([MC_REG_FAULTS_FLAGS])))
        print("ERROR " + str(arr))
        time.sleep(5)
        decodeCommandResult(sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getCOMMAND(FAULT_ACK[0]))))
        print("ERROR Cleaned")
        doit = not doit
        controller.clearEvent()

    if pad.button[button['start'][2]]:
        workState = True

    if pad.button[button['select'][2]]:
        workState = False

    if event.code == button['Y'][0] and event.value == 1:
        if DEBUG:
            print("Y pressed")
        phase = 180
        doit = not doit
        controller.clearEvent()
    elif event.code == button['A'][0] and event.value == 1:
        if DEBUG:
            print("A pressed")
        phase = 0
        doit = not doit
        controller.clearEvent()
    elif event.code == button['X'][0] and event.value == 1:
        if DEBUG:
            print("X pressed")
        phase = 90
        doit = not doit
        controller.clearEvent()
    elif event.code == button['B'][0] and event.value == 1:
        if DEBUG:
            print("B pressed")
        phase = 270
        doit = not doit
        controller.clearEvent()

    if pad.axis[button['CrossY'][2]] < 0:
        if DEBUG:
            print("Cross Y Up")
        torquemean *= speedFac
        torquemean = min([torquemean, TORQUEMAX])
    elif pad.axis[button['CrossY'][2]] > 0:
        if DEBUG:
            print("Cross Y Down")
        torquemean /= speedFac
        torquemean = max([torquemean, TORQUEMIN])

    if pad.axis[button['CrossX'][2]] > 0:
        if DEBUG:
            print("Cross X Up")
        torqueDoubleAmp *= speedFac
        torqueDoubleAmp = min([torqueDoubleAmp, AMPMAX])
    elif pad.axis[button['CrossX'][2]] < 0:
        if DEBUG:
            print("Cross X Down")
        torqueDoubleAmp /= speedFac
        torqueDoubleAmp = max([torqueDoubleAmp, AMPMIN])

    print ("Torque mean = %d, Torque double amp = %d, phase = %d" % (torquemean, torqueDoubleAmp, phase))

    if not DEBUG:
        sinParams = np.append(np.append(int32_to_int8(torquemean),int16_to_int8(torqueDoubleAmp)),int16_to_int8(phase))
        arr = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(setREG([MC_REG_TORQUE_SIN],[sinParams])))   # Set sin

    oldevent = event

    if workState != oldWorkState:
        oldWorkState = workState
        if workState:
            print("Start motor")
            if not DEBUG: decodeCommandResult(sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getCOMMAND(START_MOTOR[0]))))
            time.sleep(1)
        else:
            print("Stop motor")
            if not DEBUG: res = sendManyBytesToSerial(serial_portBG431, createDATA_PACKET(getCOMMAND(STOP_MOTOR[0])))                # Stop motor



