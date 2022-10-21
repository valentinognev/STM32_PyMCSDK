import serial
import numpy as np
import matplotlib.pyplot as plt
from IPython import get_ipython
import time
import threading

ADDSENDDELAY = True
# get_ipython().run_line_magic('matplotlib', 'qt')
# get_ipython().run_line_magic('matplotlib', 'inline')
#######################################################################################
CRC4_Lookup8 =[ 0x00, 0x02, 0x04, 0x06, 0x08, 0x0a, 0x0c, 0x0e, 0x07, 0x05, 0x03, 0x01, 0x0f, 0x0d, 0x0b, 0x09,\
                0x07, 0x05, 0x03, 0x01, 0x0f, 0x0d, 0x0b, 0x09, 0x00, 0x02, 0x04, 0x06, 0x08, 0x0a, 0x0c, 0x0e,\
                0x0e, 0x0c, 0x0a, 0x08, 0x06, 0x04, 0x02, 0x00, 0x09, 0x0b, 0x0d, 0x0f, 0x01, 0x03, 0x05, 0x07,\
                0x09, 0x0b, 0x0d, 0x0f, 0x01, 0x03, 0x05, 0x07, 0x0e, 0x0c, 0x0a, 0x08, 0x06, 0x04, 0x02, 0x00,\
                0x0b, 0x09, 0x0f, 0x0d, 0x03, 0x01, 0x07, 0x05, 0x0c, 0x0e, 0x08, 0x0a, 0x04, 0x06, 0x00, 0x02,\
                0x0c, 0x0e, 0x08, 0x0a, 0x04, 0x06, 0x00, 0x02, 0x0b, 0x09, 0x0f, 0x0d, 0x03, 0x01, 0x07, 0x05,\
                0x05, 0x07, 0x01, 0x03, 0x0d, 0x0f, 0x09, 0x0b, 0x02, 0x00, 0x06, 0x04, 0x0a, 0x08, 0x0e, 0x0c,\
                0x02, 0x00, 0x06, 0x04, 0x0a, 0x08, 0x0e, 0x0c, 0x05, 0x07, 0x01, 0x03, 0x0d, 0x0f, 0x09, 0x0b,\
                0x01, 0x03, 0x05, 0x07, 0x09, 0x0b, 0x0d, 0x0f, 0x06, 0x04, 0x02, 0x00, 0x0e, 0x0c, 0x0a, 0x08,\
                0x06, 0x04, 0x02, 0x00, 0x0e, 0x0c, 0x0a, 0x08, 0x01, 0x03, 0x05, 0x07, 0x09, 0x0b, 0x0d, 0x0f,\
                0x0f, 0x0d, 0x0b, 0x09, 0x07, 0x05, 0x03, 0x01, 0x08, 0x0a, 0x0c, 0x0e, 0x00, 0x02, 0x04, 0x06,\
                0x08, 0x0a, 0x0c, 0x0e, 0x00, 0x02, 0x04, 0x06, 0x0f, 0x0d, 0x0b, 0x09, 0x07, 0x05, 0x03, 0x01,\
                0x0a, 0x08, 0x0e, 0x0c, 0x02, 0x00, 0x06, 0x04, 0x0d, 0x0f, 0x09, 0x0b, 0x05, 0x07, 0x01, 0x03,\
                0x0d, 0x0f, 0x09, 0x0b, 0x05, 0x07, 0x01, 0x03, 0x0a, 0x08, 0x0e, 0x0c, 0x02, 0x00, 0x06, 0x04,\
                0x04, 0x06, 0x00, 0x02, 0x0c, 0x0e, 0x08, 0x0a, 0x03, 0x01, 0x07, 0x05, 0x0b, 0x09, 0x0f, 0x0d,\
                0x03, 0x01, 0x07, 0x05, 0x0b, 0x09, 0x0f, 0x0d, 0x04, 0x06, 0x00, 0x02, 0x0c, 0x0e, 0x08, 0x0a\
                ]
CRC4_Lookup4 =[  0x00, 0x07, 0x0e, 0x09, 0x0b, 0x0c, 0x05, 0x02, 0x01, 0x06, 0x0f, 0x08, 0x0a, 0x0d, 0x04, 0x03]
## MCP Commands
MCTL_SYNC  = np.uint8(0xA)
MCTL_ASYNC = np.uint8(0x9)

STC_TORQUE_MODE = 0
STC_SPEED_MODE  = 1

MCP_CMD_OK                       =0x00
MCP_CMD_NOK                      =0x01
MCP_CMD_UNKNOWN                  =0x02
MCP_DATAID_UNKNOWN               =0x03
MCP_ERROR_RO_REG                 =0x04
MCP_ERROR_UNKNOWN_REG            =0x05
MCP_ERROR_STRING_FORMAT          =0x06
MCP_ERROR_BAD_DATA_TYPE          =0x07
MCP_ERROR_NO_TXSYNC_SPACE        =0x08
MCP_ERROR_NO_TXASYNC_SPACE       =0x09
MCP_ERROR_BAD_RAW_FORMAT         =0x0A
MCP_ERROR_WO_REG                 =0x0B
MCP_ERROR_REGISTER_ACCESS        =0x0C
MCP_ERROR_CALLBACK_NOT_REGISTRED =0x0D

#    MCP_ID definition :
#    | Element Identifier 10 bits  |  Type  | Motor #|
#    |                             |        |        |
#    |15|14|13|12|11|10|09|08|07|06|05|04|03|02|01|00|

#    Type definition :
#    0	Reserved
#    1	8-bit data
#    2	16-bit data
#    3	32-bit data
#    4	Character string
#    5	Raw Structure
#    6	Reserved
#    7	Reserved
TYPE_POS = 3
ELT_IDENTIFIER_POS = 6

TYPE_DATA_SEG_END = (0 << TYPE_POS)
TYPE_DATA_8BIT    = (1 << TYPE_POS)
TYPE_DATA_16BIT   = (2 << TYPE_POS)
TYPE_DATA_32BIT   = (3 << TYPE_POS)
TYPE_DATA_STRING  = (4 << TYPE_POS)
TYPE_DATA_RAW     = (5 << TYPE_POS)
TYPE_DATA_FLAG    = (6 << TYPE_POS)
TYPE_DATA_SEG_BEG = (7 << TYPE_POS)

# /* TYPE_DATA_8BIT registers definition * /
# The list of available command from mcp.c
GET_MCP_VERSION  = [np.uint16(0x0), TYPE_DATA_32BIT]
SET_DATA_ELEMENT = [np.uint16(0x8), TYPE_DATA_8BIT]
GET_DATA_ELEMENT = [np.uint16(0x10), TYPE_DATA_8BIT]
START_MOTOR      = [np.uint16(0x18), TYPE_DATA_8BIT]
STOP_MOTOR       = [np.uint16(0x20), TYPE_DATA_8BIT]
STOP_RAMP        = [np.uint16(0x28), TYPE_DATA_8BIT]
START_STOP       = [np.uint16(0x30), TYPE_DATA_8BIT]
FAULT_ACK        = [np.uint16(0x38), TYPE_DATA_8BIT]
IQDREF_CLEAR     = [np.uint16(0x48), TYPE_DATA_8BIT]
PFC_ENABLE       = [np.uint16(0x50), TYPE_DATA_8BIT]
PFC_DISABLE      = [np.uint16(0x58), TYPE_DATA_8BIT]
PFC_FAULT_ACK    = [np.uint16(0x60), TYPE_DATA_8BIT]
GET_DBG_DATA     = [np.uint16(0x68), TYPE_DATA_8BIT]
SW_RESET         = [np.uint16(0x78), TYPE_DATA_8BIT]
MCP_USER_CMD     = [np.uint16(0x100), TYPE_DATA_8BIT]

# look in file register_interface.c in src directory for description of what registers from the list below could be written
MC_REG_STATUS                 = [np.uint16 ((1 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_CONTROL_MODE           = [np.uint16 ((2 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_RUC_STAGE_NBR          = [np.uint16 ((3 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_PFC_STATUS             = [np.uint16 ((13 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_PFC_ENABLED            = [np.uint16 ((14 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_SC_CHECK               = [np.uint16 ((15 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_SC_STATE               = [np.uint16 ((16 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_SC_STEPS               = [np.uint16 ((17 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_SC_PP                  = [np.uint16 ((18 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_SC_FOC_REP_RATE        = [np.uint16 ((19 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_SC_COMPLETED           = [np.uint16 ((20 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_POSITION_CTRL_STATE    = [np.uint16 ((21 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ),TYPE_DATA_8BIT]
MC_REG_POSITION_ALIGN_STATE   = [np.uint16 ((22 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT), TYPE_DATA_8BIT]
MC_REG_DBG_START_WRITE        = [np.uint16 ((23 << ELT_IDENTIFIER_POS) | TYPE_DATA_8BIT ), TYPE_DATA_8BIT]

# /* TYPE_DATA_16BIT registers definition * /
MC_REG_SPEED_KP               = [np.uint16 ((2   << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_SPEED_KI               = [np.uint16 ((3   << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT),TYPE_DATA_16BIT]
MC_REG_SPEED_KD               = [np.uint16 ((4   << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_KP                 = [np.uint16 ((6   << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_KI                 = [np.uint16 ((7   << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_KD                 = [np.uint16 ((8   << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_KP                 = [np.uint16 ((10  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_KI                 = [np.uint16 ((11  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_KD                 = [np.uint16 ((12  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_C1              = [np.uint16 ((13  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_C2              = [np.uint16 ((14  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_C1           = [np.uint16 ((15  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_C2           = [np.uint16 ((16  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_KI              = [np.uint16 ((17  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_KP              = [np.uint16 ((18  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FLUXWK_KP              = [np.uint16 ((19 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FLUXWK_KI              = [np.uint16 ((20 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FLUXWK_BUS             = [np.uint16 ((21 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_BUS_VOLTAGE            = [np.uint16 ((22 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_HEATS_TEMP             = [np.uint16 ((23 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_MOTOR_POWER            = [np.uint16 ((24 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_DAC_OUT1               = [np.uint16 ((25 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_DAC_OUT2               = [np.uint16 ((26 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_DAC_OUT3               = [np.uint16 ((27  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FLUXWK_BUS_MEAS        = [np.uint16 ((30 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_A                    = [np.uint16 ((31 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_B                    = [np.uint16 ((32 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_ALPHA_MEAS           = [np.uint16 ((33 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_BETA_MEAS            = [np.uint16 ((34 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_MEAS               = [np.uint16 ((35 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_MEAS               = [np.uint16 ((36 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_REF                = [np.uint16 ((37 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_REF                = [np.uint16 ((38 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_V_Q                    = [np.uint16 ((39 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_V_D                    = [np.uint16 ((40 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_V_ALPHA                = [np.uint16 ((41 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_V_BETA                 = [np.uint16 ((42 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_ENCODER_EL_ANGLE       = [np.uint16 ((43  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_ENCODER_SPEED          = [np.uint16 ((44  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_EL_ANGLE        = [np.uint16 ((45 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_ROT_SPEED       = [np.uint16 ((46 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_I_ALPHA         = [np.uint16 ((47 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_I_BETA          = [np.uint16 ((48 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_BEMF_ALPHA      = [np.uint16 ((49 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_BEMF_BETA       = [np.uint16 ((50 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_EL_ANGLE     = [np.uint16 ((51  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_ROT_SPEED    = [np.uint16 ((52  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_I_ALPHA      = [np.uint16 ((53  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_I_BETA       = [np.uint16 ((54  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_BEMF_ALPHA   = [np.uint16 ((55  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOCORDIC_BEMF_BETA    = [np.uint16 ((56  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_DAC_USER1              = [np.uint16 ((57 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_DAC_USER2              = [np.uint16 ((58 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_HALL_EL_ANGLE          = [np.uint16 ((59  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_HALL_SPEED             = [np.uint16 ((60  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FF_VQ                  = [np.uint16 ((62 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FF_VD                  = [np.uint16 ((63 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FF_VQ_PIOUT            = [np.uint16 ((64 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FF_VD_PIOUT            = [np.uint16 ((65 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_DCBUS_REF          = [np.uint16 ((66 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_DCBUS_MEAS         = [np.uint16 ((67 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_ACBUS_FREQ         = [np.uint16 ((68 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_ACBUS_RMS          = [np.uint16 ((69 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_I_KP               = [np.uint16 ((70 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_I_KI               = [np.uint16 ((71 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_I_KD               = [np.uint16 ((72 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_V_KP               = [np.uint16 ((73 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_V_KI               = [np.uint16 ((74 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_V_KD               = [np.uint16 ((75 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_STARTUP_DURATION   = [np.uint16 ((76 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_SC_PWM_FREQUENCY       = [np.uint16 ((77  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_POSITION_KP            = [np.uint16 ((78  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_POSITION_KI            = [np.uint16 ((79  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_POSITION_KD            = [np.uint16 ((80  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_SPEED_KP_DIV           = [np.uint16 ((81  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_SPEED_KI_DIV           = [np.uint16 ((82  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_SPEED_KD_DIV           = [np.uint16 ((83  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_KP_DIV             = [np.uint16 ((84  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_KI_DIV             = [np.uint16 ((85  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_D_KD_DIV             = [np.uint16 ((86  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_KP_DIV             = [np.uint16 ((87  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_KI_DIV             = [np.uint16 ((88  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_I_Q_KD_DIV             = [np.uint16 ((89  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_POSITION_KP_DIV        = [np.uint16 ((90  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_POSITION_KI_DIV        = [np.uint16 ((91  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_POSITION_KD_DIV        = [np.uint16 ((92  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_I_KP_DIV           = [np.uint16 ((93  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_I_KI_DIV           = [np.uint16 ((94  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_I_KD_DIV           = [np.uint16 ((95  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_V_KP_DIV           = [np.uint16 ((96  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_V_KI_DIV           = [np.uint16 ((97  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PFC_V_KD_DIV           = [np.uint16 ((98  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_KI_DIV          = [np.uint16 ((99  << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STOPLL_KP_DIV          = [np.uint16 ((100 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FLUXWK_KP_DIV          = [np.uint16 ((101 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_FLUXWK_KI_DIV          = [np.uint16 ((102 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_STARTUP_CURRENT_REF    = [np.uint16 ((105 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]
MC_REG_PULSE_VALUE            = [np.uint16 ((106 << ELT_IDENTIFIER_POS) | TYPE_DATA_16BIT ),TYPE_DATA_16BIT]

# /* TYPE_DATA_32BIT registers definition * /
MC_REG_FAULTS_FLAGS           = [np.uint16 ((0 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SPEED_MEAS             = [np.uint16 ((1 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SPEED_REF              = [np.uint16 ((2 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_STOPLL_EST_BEMF        = [np.uint16 ((3 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_STOPLL_OBS_BEMF        = [np.uint16 ((4 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_STOCORDIC_EST_BEMF     = [np.uint16 ((5 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_STOCORDIC_OBS_BEMF     = [np.uint16 ((6 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_FF_1Q                  = [np.uint16 ((7 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_FF_1D                  = [np.uint16 ((8 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_FF_2                   = [np.uint16 ((9 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT] #/* To be checked shifted by >> 16*/
MC_REG_PFC_FAULTS             = [np.uint16 ((40 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_CURRENT_POSITION       = [np.uint16 ((41 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_RS                  = [np.uint16 ((91 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_LS                  = [np.uint16 ((92 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_KE                  = [np.uint16 ((93 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_VBUS                = [np.uint16 ((94 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_MEAS_NOMINALSPEED   = [np.uint16 ((95 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_CURRENT             = [np.uint16 ((96 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_SPDBANDWIDTH        = [np.uint16 ((97 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_LDLQRATIO           = [np.uint16 ((98 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_NOMINAL_SPEED       = [np.uint16 ((99 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_CURRBANDWIDTH       = [np.uint16 ((100 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_J                   = [np.uint16 ((101 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_F                   = [np.uint16 ((102 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_MAX_CURRENT         = [np.uint16 ((103 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_STARTUP_SPEED       = [np.uint16 ((104 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_SC_STARTUP_ACC         = [np.uint16 ((105 << ELT_IDENTIFIER_POS) | TYPE_DATA_32BIT ),TYPE_DATA_32BIT]
MC_REG_FW_NAME               = [ np.uint16((0 << ELT_IDENTIFIER_POS) | TYPE_DATA_STRING), TYPE_DATA_STRING]
MC_REG_CTRL_STAGE_NAME       = [np.uint16 ((1 << ELT_IDENTIFIER_POS) | TYPE_DATA_STRING ),TYPE_DATA_STRING]
MC_REG_PWR_STAGE_NAME        = [np.uint16 ((2 << ELT_IDENTIFIER_POS) | TYPE_DATA_STRING ),TYPE_DATA_STRING]
MC_REG_MOTOR_NAME            = [np.uint16 ((3 << ELT_IDENTIFIER_POS) | TYPE_DATA_STRING ),TYPE_DATA_STRING]

MC_REG_GLOBAL_CONFIG         = [np.uint16 ((0 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_MOTOR_CONFIG          = [np.uint16 ((1 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_APPLICATION_CONFIG    = [np.uint16 ((2 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_FOCFW_CONFIG          = [np.uint16 ((3 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_SPEED_RAMP            = [np.uint16 ((6 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_TORQUE_RAMP           = [np.uint16 ((7 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_REVUP_DATA            = [np.uint16 ((8 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW] #/* Configure all steps*/
MC_REG_CURRENT_REF           = [np.uint16 ((13 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_POSITION_RAMP         = [np.uint16 ((14 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_ASYNC_UARTA           = [np.uint16 ((20 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_ASYNC_UARTB           = [np.uint16 ((21 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_ASYNC_STLNK           = [np.uint16 ((22 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW ),TYPE_DATA_RAW]
MC_REG_SPEED_SIN             = [np.uint16 ((23 << ELT_IDENTIFIER_POS) | TYPE_DATA_RAW),TYPE_DATA_RAW]

SERIAL_READ_DATA=[]
#######################################################################################
def int32_to_int8(n):
    mask = (1 << 8) - 1
    return [(n >> k) & mask for k in range(0, 32, 8)]
#######################################################################################
def int16_to_int8(n):
    mask = (1 << 8) - 1
    return [(n >> k) & mask for k in range(0, 16, 8)]
#######################################################################################
def ComputeHeaderCRC(header):
  crc = np.uint8(0)

  header &= 0x0fffffff

  crc = CRC4_Lookup8[crc ^ np.uint8(header         & 0xff)]
  crc = CRC4_Lookup8[crc ^ np.uint8((header >> 8)  & 0xff)]
  crc = CRC4_Lookup8[crc ^ np.uint8((header >> 16) & 0xff)]
  crc = CRC4_Lookup4[crc ^ np.uint8((header >> 24) & 0x0f)]

  header |= np.uint32(crc) << 28
  return header
#######################################################################################
def CheckHeaderCRC(header):
    crc = 0
    crc = CRC4_Lookup8[crc ^ np.uint8(header & 0xff)]
    crc = CRC4_Lookup8[crc ^ np.uint8((header >> 8) & 0xff)]
    crc = CRC4_Lookup8[crc ^ np.uint8((header >> 16) & 0xff)]
    crc = CRC4_Lookup8[crc ^ np.uint8((header >> 24) & 0xff)]
    return crc == 0
#######################################################################################
def computeCRC8(bb):

    sum = 0
    for b in bb:
        sum = CRC4_Lookup8[sum ^ b & 0xFF]

    res = sum & 0xFF
    res += sum >> 8
    return res
#######################################################################################
def getByteArray(arr):
    data=np.array(arr, np.uint8)
    data = (np.append(data,computeCRC8(data))).tolist()
    databy = bytearray(data)
    return databy
#######################################################################################


class SerialThread(threading.Thread):
    def __init__(self, serial_port, length = 4):
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
        res = serial_port.read(self.length)
        line = []
        for c in res:
            line.append(c)
        self.serial_read_data = np.array(line, np.uint8)
        self.finished = True

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
def send4BytesToSerial(serial_port, dataList):
    readSerialThread = SerialThread(serial_port, 4)
    readSerialThread.start()
    serial_port.write(dataList)
    while not readSerialThread.isFinished():
        pass
    # res = readUINT32fromSerial(serial_port)
    res = readSerialThread.getSerialData().view(np.uint32)[0]
    if CheckHeaderCRC(res):
        return res
    return []
#######################################################################################
def sendManyBytesToSerial(serial_port, dataList):
    readSerialThread = SerialThread(serial_port, 10000)
    readSerialThread.start()
    if ADDSENDDELAY:
        serial_port.write(dataList[:4])
        time.sleep(.01)
        serial_port.write(dataList[4:])
    else:
        serial_port.write(dataList)
    while not readSerialThread.isFinished():
        pass
    # res = readUINT32fromSerial(serial_port)
    serial_data = readSerialThread.getSerialData()
    return serial_data
#######################################################################################
def decodeRegValues(serial_data, regs):
    if len(serial_data) == 0:
        return []
    res = serial_data[0:4].view(np.uint32)[0]
    if  len(serial_data)<=4 or not CheckHeaderCRC(res):
        return []
    dataLength, sync = getDataLength(res)
    arr = serial_data[4:]
    regResults = []
    ind = 0
    for reg in regs:
        if reg[1] == TYPE_DATA_8BIT:
            regResults.append(arr[ind])
            ind += 1
        elif reg[1] == TYPE_DATA_16BIT:
            regResults.append(arr[ind:ind+2].view(np.uint16)[0])
            ind += 2
        elif reg[1] == TYPE_DATA_32BIT:
            regResults.append(arr[ind:ind+4].view(np.uint32)[0])
            ind += 4
        else:    
            print ('Register cannot be included in the list and must be decoded separately')
            raise 'Register cannot be included in the list and must be decoded separately'
    return regResults
#######################################################################################
def decodeCommandResult(serial_data, type=TYPE_DATA_8BIT):
    if len(serial_data) == 0:
        return []
    res = serial_data[0:4].view(np.uint32)[0]
    if not CheckHeaderCRC(res):
        return []

    dataLength, sync = getDataLength(res)
    arr = np.array(serial_data[4:], np.uint8)
    if len(arr) != dataLength:
        return []

    if type == TYPE_DATA_8BIT:
        return arr
    elif type == TYPE_DATA_32BIT:
        res = arr[0:(len(arr)//4)*4].view(np.uint32)
        return res
#######################################################################################
def getDataLength(res32):
    length = (res32 >> 4) & 0x1FFF
    syncasync =  res32 & 0b1111
    return length, syncasync
#######################################################################################
def getBEACON(version = 0, RX_maxSize = 7, TXS_maxSize = 7, TXA_maxSize = 32):
    beacon = 0x05
    beacon |= version << 4
    beacon |= RX_maxSize << 8
    beacon |= TXS_maxSize << 14
    beacon |= TXA_maxSize << 21
    return np.array(int32_to_int8(ComputeHeaderCRC(np.uint32(beacon))),np.uint8)
#######################################################################################
def decodeBEACON(res32):
    beacon = 0x05    
    if res32 & 0b1111 != beacon:
        return []
  
    version = (res32 >> 4) & 0b111
    DATA_CRC = (res32 >> 7) & 0b1
    RX_maxSize = (res32 >> 8) & 0b111111
    TXS_maxSize = (res32 >> 14) & 0b1111111
    TXA_maxSize = (res32 >> 21) & 0b1111111
    return version, DATA_CRC, RX_maxSize, TXS_maxSize, TXA_maxSize
#######################################################################################
def getPING(cbit = 0, Nbit = 0, ipID = 0, packetNumber = 0):
    ping = 0x06
    ping |= cbit << 4
    ping |= cbit << 5
    ping |= Nbit << 6
    ping |= Nbit << 7
    ping |= ipID << 8
    ping |= packetNumber << 12   
    return np.array(int32_to_int8(ComputeHeaderCRC(np.uint32(ping))),np.uint8)
#######################################################################################
def decodePING(res32):
    ping = 0x06
    if res32 & 0b1111 != ping:
        return []
    cbit = (res32 >> 4) & 0b1
    Nbit = (res32 >> 6) & 0b1
    ipID = (res32 >> 8) & 0b1111
    packetNumber = (res32 >> 12) & 0xFFFF
    return packetNumber, ipID, cbit, Nbit
#######################################################################################
def createDATA_PACKET( command):
    data_packet = 0x09
    data_packet |= (len(command) << 4) & 0x1FFF0
    header = np.array(int32_to_int8(ComputeHeaderCRC(np.uint32(data_packet))), np.uint8)
    return np.append(header,command)
#######################################################################################
def getCOMMAND(command, motorID = 1):
    command |= motorID
    return np.array(int16_to_int8(command), np.uint8)
#######################################################################################
def getREG(regs, motorID = 1):
    regRequest = getCOMMAND(GET_DATA_ELEMENT[0], motorID)
    for reg in regs:
        reg[0] |= motorID
        reg[0] |= reg[1]
        regRequest = np.append(regRequest,np.array(int16_to_int8(reg[0]), np.uint8))
    return regRequest
#######################################################################################
def setREG(regs, values, motorID = 1):
    regRequest = getCOMMAND(SET_DATA_ELEMENT[0], motorID)
    for ind in range(len(regs)):
        reg = regs[ind]
        reg[0] |= motorID
        reg[0] |= reg[1]
        regRequest = np.append(regRequest,np.array(int16_to_int8(reg[0]), np.uint8))
        if reg[1] == TYPE_DATA_8BIT:
            if len(values[ind])>0:
                regRequest = np.append(regRequest, values[ind])
        elif reg[1] == TYPE_DATA_16BIT:
            regRequest = np.append(regRequest, np.array(int16_to_int8(values[ind]), np.uint8))
        elif reg[1] == TYPE_DATA_32BIT:
            regRequest = np.append(regRequest, np.array(int32_to_int8(values[ind]), np.uint8))
        elif reg[1] == TYPE_DATA_STRING:
            regRequest = np.append(regRequest, np.array(values[ind], np.uint8))
        elif reg[1] == TYPE_DATA_RAW:
            regRequest = np.append(regRequest, np.array(int16_to_int8(len(values[ind])), np.uint8))
            regRequest = np.append(regRequest, values[ind])

    return np.array(regRequest, np.uint8)
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
decodeCommandResult(sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(START_MOTOR[0]))))
time.sleep(1)

rpmmean = 2000
rpmamp = 200
phase = 0
sinParams = np.append(np.append(int32_to_int8(rpmmean),int16_to_int8(rpmamp)),int16_to_int8(phase))
arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(setREG([MC_REG_SPEED_SIN],[sinParams])))

arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(setREG([MC_REG_DBG_START_WRITE],[[]])))
res = sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(STOP_MOTOR[0])))
decodeCommandResult(res)

arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(getCOMMAND(GET_DBG_DATA[0])))


# arr = sendManyBytesToSerial(serial_port, createDATA_PACKET(getREG([MC_REG_STOPLL_EL_ANGLE, MC_REG_SPEED_REF])))
# data = decodeRegValues(arr, [MC_REG_STOPLL_EL_ANGLE, MC_REG_SPEED_REF])


FFOC = 2000
elToMech = 7
contElAngle = np.zeros(len(elAngle))
counter=0
for i in range(len(elAngle)-1):
    contElAngle[i] = elAngle[i]-(-2**15)+(2**16)*counter
    if elAngle[i+1]<elAngle[i]:
        counter += 1
angleFromEl = contElAngle/elToMech/(2**16)*360
elVelHz = np.diff(angleFromEl)*FFOC/360*10

inds = range(0,300)
plt.plot(contElAngle[inds]-contElAngle[inds[0]], speedRef[inds])
plt.plot(contElAngle[inds]-contElAngle[inds[0]], elVelHz[inds])
plt.grid(True)
plt.show()

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
    
#     angle = arr[:1024]
#     tarSpeed = arr[1024:2048]
    
#     FFOC = 2000
#     elToMech = 7
#     elangle = arr[2048:]
    
#     contAngle = np.zeros(len(angle))
#     counter=0
#     for i in range(len(angle)-1):
#         contAngle[i] = angle[i]-(-2**15)+(2**16)*counter
#         if angle[i+1]<angle[i]:
#             counter += 1
#     contAngle = contAngle/(2**16)*360     
#     contAngleVelHz = np.diff(contAngle)*FFOC/360*10
#     contAngleVelHz[contAngleVelHz>1000]=500;
#     # contElAngle = np.zeros(len(elangle))
#     # counter=0;
#     # for i in range(len(elangle)-1):
#     #     contElAngle[i] = elangle[i]-(-2**15)+(2**16)*counter
#     #     if elangle[i+1]<elangle[i]:
#     #         counter += 1
#     # angleFromEl = contElAngle/elToMech/(2**16)*360
#     # elVelHz = np.diff(angleFromEl)*FFOC/360*10

#     inds = range(0,300)
#     plt.plot(contAngle[inds]-contAngle[inds[0]],tarSpeed[inds])
#     plt.plot(contAngle[inds]-contAngle[inds[0]],contAngleVelHz[inds])
#     plt.grid(True)
#     plt.show()
#     #plt.pause(0.0001)
#     #input("Press Enter to continue...")
    
# ser.close()
# pass