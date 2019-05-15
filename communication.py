import serial
import sys
import time


if __name__ == '__main__': 
    dataBytes = 0
    buf = b''
    index = 0
    vr = 0
    vd = 0
    try:
        com = serial.Serial('/dev/ttyACM1', 115200)
    except:
        print("Couldn't stabilish connection with serial port!")
        sys_exit(0)
    
    #com.read(10) 
    while True:
        
        while b'\x0c' not in buf:
            buf += com.read(com.inWaiting())
        
        if buf[0] == 0x40:
            print(buf)
            index = buf.index(b'\xa8')
            vr = int(buf[1:index], 10)
            vd = int(buf[index + 1:len(buf)-1], 10)
            buf = b''
        else:
            print("Wrong format received: {}".format(buf))
            buf = b''
            #buf += com.read(com.inWaiting())
        
        print("Left speed: {} RPS\nRight speed: {} RPS".format(vr, vd))
        buf = b''
        
        #time.sleep(0.0001)
        #data = com.read(2)
        #if dataBytes > 0:
            #received = com.read(dataBytes)

