from pyftdi.gpio import (GpioAsyncController,
                         GpioSyncController,
                         GpioMpsseController)

PI=3.1415

class AS5047Diagnostics:
    #    uint16_t 
    agc = 0   #: 8;
    lf = 0    #: 1;
    cof = 0   #: 1;
    magh = 0  #: 1;
    magl = 0  #: 1;
    reg = 0 

class AS5047ZPosM :
    zposm = 0#: 8;     };
    reg = 0 

class AS5047ZPosL:
    zposl = 0 #: 6;
    comp_l_error_en = 0 #: 1;
    comp_h_error_en = 0 #: 1; 
    reg = 0 

class AS5047Settings1:
    reserved = 0 #: 1;
    noiseset = 0 #: 1;
    dir = 0 #: 1;
    uvw_abi = 0 #: 1;
    daecdis = 0 #: 1;
    abibin = 0 #: 1;
    dataselect = 0 #: 1;
    pwmon = 0 #: 1;     };
    reg = 0 

class AS5047Settings2:
    uvwpp = 0 #: 3;
    hys = 0 #: 2;
    abires = 0 #: 3;     };
    reg = 0 

class AS5047Error :
    framingError = False
    commandInvalid = False
    parityError = False

AS5047_CPR = 16384
AS5047_ANGLECOM_REG = 0x3FFF
AS5047_ANGLEUNC_REG = 0x3FFE
AS5047_MAGNITUDE_REG = 0x3FFD
AS5047_DIAGNOSTICS_REG = 0x3FFC
AS5047_ERROR_REG = 0x0001
AS5047_PROG_REG = 0x0003
AS5047_ZPOSM_REG = 0x0016
AS5047_ZPOSL_REG = 0x0017
AS5047_SETTINGS1_REG = 0x0018
AS5047_SETTINGS2_REG = 0x0019

AS5047_PARITY = 0x8000
AS5047_RW = 0x4000
AS5047_ERRFLG = 0x4000
AS5047_RESULT_MASK = 0x3FFF

PINMOSI = 0
PINMISO = 1
PINCLK  = 2
PINCS   = 3

def init():
    spi = GpioAsyncController()
    spi.configure('ftdi:///1', direction=0xF0)
    return spi

 # Use for SPI timing's delay function
 # It's only test on STM32F405/F407 168MHz
def spi_delay()
    for i in range(10):
        pass

# SPI transfer 16 bit value
def spi_transfer(txdata)
    rxdata = 0;

    for (int i = 0; i < 16; i++)
    {
    	HAL_GPIO_WritePin(SDI_GPIO_Port, SDI_Pin, bitRead(txdata, 15 - i));
    	HAL_GPIO_WritePin(SCL_GPIO_Port, SCL_Pin, GPIO_PIN_SET);
        spi_delay();
        HAL_GPIO_WritePin(SCL_GPIO_Port, SCL_Pin, GPIO_PIN_RESET);
        bitWrite(rxdata, 15 - i, HAL_GPIO_ReadPin(SDO_GPIO_Port, SDO_Pin));
        spi_delay();
    }
    return rxdata;
}

def spi_transfer16(outdata) :
    if (nCS >= 0)
          digitalWrite(nCS, 0)
    spi -> beginTransaction(settings)
    uint16_t result = spi -> transfer16(outdata)
    spi -> endTransaction()
    if (nCS >= 0)
          digitalWrite(nCS, 1)
    # TODO check parity
    errorflag = ((result & AS5047_ERRFLG) > 0)
    return result

def getCurrentAngle():
    readCorrectedAngle()
    return readCorrectedAngle()/AS5047_CPR * 2 * PI

def getFastAngle():
    return readCorrectedAngle()/AS5047_CPR * 2 * PI

def readRawAngle():
    command = AS5047_ANGLEUNC_REG | AS5047_RW
    # set r = 1 and parity = 0, result is 0x7FFE
    lastresult = spi_transfer16(command) & AS5047_RESULT_MASK
    return lastresult

def readCorrectedAngle():
    command = AS5047_ANGLECOM_REG | AS5047_PARITY | AS5047_RW
    # set r = 1 and parity = 1, result is 0xFFFF
    lastresult = spi_transfer16(command) & AS5047_RESULT_MASK
    return lastresult

def readMagnitude():
    command = AS5047_MAGNITUDE_REG | AS5047_RW
    # set r = 1, result is 0x7FFD
    cmdresult = spi_transfer16(command)
    result = nop()
    return result

def isErrorFlag():
    return errorflag

def clearErrorFlag():
    command = AS5047_ERROR_REG | AS5047_RW
    # set r = 1, result is 0x4001
    cmdresult = spi_transfer16(command)
    result = nop()
    err = AS5047Error
    err.framingError = ((result & 0x0001) != 0x0000),
    err.commandInvalid = ((result & 0x0002) != 0x0000),
    err.parityError = ((result & 0x0004) != 0x0000)    
    return err

def readSettings1():
    command = AS5047_SETTINGS1_REG | AS5047_PARITY | AS5047_RW
    # set r = 1, result is 0xC018
    cmdresult = spi_transfer16(command)
    result = AS5047Settings1
    result.reg = nop()
    return result

def writeSettings1(AS5047Settings1 settings):
    command = AS5047_SETTINGS1_REG
    # set r = 0, result is 0x0018
    cmdresult = spi_transfer16(command)
    cmdresult = spi_transfer16(settings.reg)

def readSettings2():
    command = AS5047_SETTINGS2_REG | AS5047_RW
    # set r = 1, result is 0x4019
    cmdresult = spi_transfer16(command)
    result = AS5047Settings2 
    result.reg = nop()
    return result

def readDiagnostics():
    command = AS5047_DIAGNOSTICS_REG | AS5047_PARITY | AS5047_RW
    # set r = 1, result is 0xFFFC
    cmdresult = spi_transfer16(command)
    result = AS5047Diagnostics
    result.reg = nop()
    return result

def enablePWM(enable):
    settings = readSettings1()
    settings.pwmon = enable
    writeSettings1(settings)

def enableABI(enable):
    settings = readSettings1()
    settings.uvw_abi = 0 if enable else 1
    writeSettings1(settings)

def setZero(value):
    # TODO implement me!
    return 0

def nop():
    result = spi_transfer16(0xFFFF)
    # using 0xFFFF as nop instead of 0x0000, then next call to fastAngle will return an angle
    return result & AS5047_RESULT_MASK


