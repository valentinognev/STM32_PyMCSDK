from pyftdi.gpio import (GpioAsyncController,
                         GpioSyncController,
                         GpioMpsseController)

gpio = GpioAsyncController()
gpio.configure('ftdi:///1', direction=0xF0)
# all output set low
enTable=[10, 13, 11, 12]
oldRes=0
oldEn = 0
val = 0
while 1:
    res = gpio.read()
    en = enTable[res & 0x03]
    
    if res &0x04 != 0:
        print("NOW***************************")
    if en != oldEn:
        delta = (en-oldEn)
        if delta == 1 | delta == -3:
            val += 1
        else:
            val -= 1
        oldEn = en
        print(bin(res & 0x03)+' '+str(en)+' '+str(val))
gpio.close()