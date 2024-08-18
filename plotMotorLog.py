from matplotlib import pyplot as plt
import numpy as np


#######################################################################################
def intAngleToContinousAngle(angle, minValue, valSize):
    contAngle = np.zeros(len(angle))
    counter = 0
    for i in range(len(angle)-1):
        contAngle[i] = angle[i] - minValue + valSize*counter
        if angle[i+1] < angle[i]:
            counter += 1
    contAngle = contAngle/valSize*360
    return contAngle
#######################################################################################
def readDataFromFile(fileName):
    # read hole file
    f = open(fileName, 'r')
    fdata = f.readlines()
    f.close()
    # combile all data to single line ith space as separator
    fdata = ''.join(fdata)
    #remove all new lines
    fdata = fdata.replace('\n', ' ')
    # split the data by separator
    separator = '[2048]'
    fdata = fdata.split(separator)
    if len(fdata[0]) < 2:
        fdata = fdata[1:]

    # split by space and conver to integer
    for i in range(len(fdata)):
        fdata[i] = fdata[i].split(' ')
        if len(fdata[i][0]) < 2:
            fdata[i] = fdata[i][1:]
        if len(fdata[i][-1]) < 2:
            fdata[i] = fdata[i][:-1]    
        fdata[i]=np.array(fdata[i]).astype(int)
        pass
    
    return fdata

#######################################################################################
def main():
    f4data = readDataFromFile('motorLogNeutral.txt')


    mecAngle = f4data[0]
    torqueRef = f4data[1]
    elAngle = f4data[2]
    encAngle = f4data[3]

    SPEED_LOOP_FREQUENCY_HZ = 1000
    elToMech = 12

    mecContAngle = intAngleToContinousAngle(mecAngle, -2**15, 2**16)
    elContAngle = intAngleToContinousAngle(elAngle, -2**15, 2**16)/elToMech
    encContAngle = intAngleToContinousAngle(encAngle, 0, 2000)
    contMecAngleSpeedHz = np.diff(mecContAngle)*SPEED_LOOP_FREQUENCY_HZ/360
    contElAngleSpeedHz = np.diff(elContAngle)*SPEED_LOOP_FREQUENCY_HZ/360
    contEncAngleSpeedHz = np.diff(encContAngle)*SPEED_LOOP_FREQUENCY_HZ/360
    window = 3
    # elVelHz = np.diff(angleFromEl)*FFOC/360*10

    inds = range(0,900)
    # plt.subplot(2,1,1)
    plt.plot(elContAngle[inds]-elContAngle[inds[0]], contMecAngleSpeedHz[inds]*60, 'x-')
    plt.plot(elContAngle[inds]-elContAngle[inds[0]], contElAngleSpeedHz[inds]*60,'-o')
    plt.plot(elContAngle[inds]-elContAngle[inds[0]], contEncAngleSpeedHz[inds]*60,'-o')
    plt.plot(elContAngle[inds]-elContAngle[inds[0]], torqueRef[inds],'-o')
    # plt.plot(encContAngle[inds]-encContAngle[inds[0]], contEncAngleSpeedHz[inds]*60,'-o')
    plt.ylabel('RPM')
    plt.xlabel('angle [deg]')
    plt.grid(True)
    plt.legend(['Mechanical', 'Electrical', 'Encoder', 'Torque'])
    # plt.subplot(2,1,2)
    plt.show()
    pass
#######################################################################################
if __name__ == '__main__':
    main()